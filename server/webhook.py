"""
FastAPI server exposing a webhook to trigger the RAG assistant chain.
"""
from fastapi import FastAPI, Request
from generate.thread import generate_tweet_thread
from rag.query import get_context_for_question

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    """
    Accepts a JSON payload with a 'topic', runs the RAG chain, and returns the generated thread.
    """
    data = await request.json()
    topic = data.get("topic", "")
    # TODO: Add error handling and authentication
    context = get_context_for_question(topic)
    thread = generate_tweet_thread(context)
    return {"thread": thread} 