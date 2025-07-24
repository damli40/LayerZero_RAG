import os
from telegram import Update
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.query import ask_question
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from generate.thread import generate_thread
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()  # Make sure you have .env with TELEGRAM_BOT_TOKEN

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Or replace with your token string

user_last_asked = {}  # <-- Move to global scope

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the Omnichain Assistant! Type your question or /thread to generate content.")

# Handle /thread command
async def thread_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args if hasattr(context, 'args') else []
    if args: 
        topic = " ".join(args)
    else:
        await update.message.reply_text("Please provide a topic after /thread, e.g. /thread LayerZero stablecoins")
        return
    await update.message.reply_text(f"Generating content thread for: {topic} ...")
    thread = generate_thread(topic)
    await update.message.reply_text(thread)

# Handle any text message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.utcnow()

    last_time = user_last_asked.get(user_id)
    if last_time and (now - last_time) < timedelta(seconds=30):
        await update.message.reply_text("⏱ Please wait 30 seconds before asking again.")
        return

    user_last_asked[user_id] = now
    user_input = update.message.text
    await update.message.reply_text("🔍 Searching LayerZero knowledge base...")
    response = ask_question(user_input)
    await update.message.reply_text(response)

# Main app loop
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("thread", thread_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
