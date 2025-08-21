# bot.py
import os
import sys
import asyncio
import contextlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from generate.thread import generate_thread
from rag.query import query_rag

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

REQUEST_TIMEOUT_SECONDS = 60
RETRY_ON_TIMEOUT = 1


async def _typing_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, interval_seconds: float = 5.0):
    try:
        while True:
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        return


async def _run_blocking_with_timeout(func, *args, timeout_seconds: int = REQUEST_TIMEOUT_SECONDS):
    loop = asyncio.get_running_loop()
    return await asyncio.wait_for(loop.run_in_executor(None, lambda: func(*args)), timeout=timeout_seconds)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Omnichain Assistant.\n\n"
        "Commands:\n"
        "/start - Show this help\n"
        "/thread <topic> - Generate a Twitter thread\n"
        "/help - Show help\n\n"
        "Just type your question about LayerZero and I'll help you."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Omnichain Assistant Help\n\n"
        "Commands:\n"
        "- /thread <topic> - Generate a Twitter thread about a topic\n"
        "- /help - Show this help\n\n"
        "Features:\n"
        "- Ask questions about LayerZero ecosystem\n"
        "- Get source citations for all answers\n"
        "- Rate limiting for fair usage\n"
        "- Confidence scoring for response quality\n\n"
        "Example:\n"
        "What is DVN in LayerZero?\n"
        "/thread  OFTs explained"
    )


async def thread_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args if hasattr(context, 'args') else []

    if not args:
        await update.message.reply_text(
            "Please provide a topic after /thread\n\n"
            "Example: /thread LayerZero and stablecoins"
        )
        return

    topic = " ".join(args)

    loading_message = await update.message.reply_text("Generating thread. This may take up to a minute...")
    typing_task = asyncio.create_task(_typing_loop(context, update.effective_chat.id))

    try:
        attempt = 0
        last_error_text = None
        while True:
            try:
                thread_content = await _run_blocking_with_timeout(generate_thread, topic, timeout_seconds=REQUEST_TIMEOUT_SECONDS)
                sources_result = await _run_blocking_with_timeout(
                    query_rag,
                    topic,
                    user_id,
                    "telegram",
                    timeout_seconds=REQUEST_TIMEOUT_SECONDS,
                )
                break
            except asyncio.TimeoutError:
                attempt += 1
                if attempt <= RETRY_ON_TIMEOUT:
                    await loading_message.edit_text("Request timed out. Retrying once...")
                    continue
                last_error_text = "Request timed out. Please try again later."
                raise
            except Exception as exc:
                last_error_text = f"An error occurred: {str(exc)}"
                raise

        confidence = sources_result.get("confidence_score", 0.0) if isinstance(sources_result, dict) else 0.0
        processing_time = sources_result.get("processing_time_ms", 0) if isinstance(sources_result, dict) else 0
        sources = sources_result.get("sources", []) if isinstance(sources_result, dict) else []

        response_parts = []
        response_parts.append("Thread Generated\n")
        response_parts.append(thread_content)
        # Hide metadata in user-facing thread output

        full_response = "".join(response_parts)

        if len(full_response) > 4096:
            await loading_message.edit_text("Response is long; sending in parts...")
            await update.message.reply_text(thread_content)
            # No metadata block
        else:
            await loading_message.edit_text(full_response)

    except Exception as e:
        error_text = last_error_text or "An unexpected error occurred. Please try again."
        try:
            await loading_message.edit_text(error_text)
        except Exception:
            await update.message.reply_text(error_text)
        print(f"Error in thread_command: {str(e)}")
    finally:
        typing_task.cancel()
        with contextlib.suppress(Exception):
            await typing_task


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_input = update.message.text

    loading_message = await update.message.reply_text("Processing your request. This may take up to a minute...")
    typing_task = asyncio.create_task(_typing_loop(context, update.effective_chat.id))

    try:
        attempt = 0
        last_error_text = None
        while True:
            try:
                result = await _run_blocking_with_timeout(
                    query_rag,
                    user_input,
                    user_id,
                    "telegram",
                    timeout_seconds=REQUEST_TIMEOUT_SECONDS,
                )
                break
            except asyncio.TimeoutError:
                attempt += 1
                if attempt <= RETRY_ON_TIMEOUT:
                    await loading_message.edit_text("Request timed out. Retrying once...")
                    continue
                last_error_text = "Request timed out. Please try again later."
                raise
            except Exception as exc:
                last_error_text = f"An error occurred: {str(exc)}"
                raise

        if not isinstance(result, dict) or not result.get("success", False):
            error_msg = (result or {}).get("response", "Unknown error occurred") if isinstance(result, dict) else "Unknown error occurred"
            await loading_message.edit_text(error_msg)
            return

        response_text = result.get("response", "")
        # Hide confidence/sources in user-facing responses
        full_response = response_text

        if len(full_response) > 4096:
            await loading_message.edit_text("Response is long; sending in parts...")
            await update.message.reply_text(response_text)
        else:
            await loading_message.edit_text(full_response)

    except Exception as e:
        error_text = last_error_text or "An unexpected error occurred. Please try again."
        try:
            await loading_message.edit_text(error_text)
        except Exception:
            await update.message.reply_text(error_text)
        print(f"Error in handle_message: {str(e)}")
    finally:
        typing_task.cancel()
        with contextlib.suppress(Exception):
            await typing_task


def main():
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()

            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("thread", thread_command))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            print("Telegram bot is running with guardrails...")
            print("Timeouts configured and auto-restart enabled")

            app.run_polling(
                poll_interval=3.0,
                timeout=60,
                bootstrap_retries=10,
                read_timeout=60,
                write_timeout=60,
                connect_timeout=60,
                pool_timeout=60,
                drop_pending_updates=True,
            )

        except Exception as e:
            retry_count += 1
            print(f"Bot crashed (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                print("Restarting bot in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print("Max retries reached. Bot failed to start.")
                break


if __name__ == "__main__":
    main()
