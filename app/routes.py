from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.query import query_rag
from generate.thread import generate_thread

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, question: str = Form(...)):
    answer = query_rag(question)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "question": question,
        "answer": answer
    })

@router.post("/thread", response_class=HTMLResponse)
async def thread(request: Request, topic: str = Form(...)):
    thread = generate_thread(topic)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "thread": thread,
        "question": topic
    })
