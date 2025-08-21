from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.query import query_rag, check_qdrant_ready
from generate.thread import generate_thread
from rag.metadata_db import get_metadata_db
from rag.guardrails import get_guardrails

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, question: str = Form(...)):
    start_time = time.time()
    
    # Get client IP for user identification
    client_ip = request.client.host if request.client else "unknown"
    
    # Enhanced query with guardrails
    result = query_rag(
        question=question,
        user_id=client_ip,
        client_type="web"
    )
    
    processing_time = int((time.time() - start_time) * 1000)
    
    if not result.get("success", False):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "question": question,
            "answer": f"Error: {result.get('response', 'Unknown error')}",
            "error": True
        })
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "question": question,
        "answer": result["response"],
        "confidence": result.get("confidence_score", 0.0),
        "processing_time": processing_time,
        "sources": result.get("sources", [])
    })

@router.post("/thread", response_class=HTMLResponse)
async def thread(request: Request, topic: str = Form(...)):
    start_time = time.time()
    
    # Get client IP for user identification
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Generate thread content
        thread_content = generate_thread(topic)
        
        # Get sources separately for the topic (not the thread generation process)
        sources_result = query_rag(
            question=topic,
            user_id=client_ip,
            client_type="web"
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "thread": thread_content,
            "question": topic,
            "confidence": sources_result.get("confidence_score", 0.0),
            "processing_time": processing_time,
            "sources": sources_result.get("sources", [])
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "question": topic,
            "answer": f"Error generating thread: {str(e)}",
            "error": True
        })

@router.get("/analytics", response_class=JSONResponse)
async def get_analytics(days: int = 30):
    """Get usage analytics."""
    try:
        metadata_db = get_metadata_db()
        analytics = metadata_db.get_usage_analytics(days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/ready", response_class=JSONResponse)
async def readiness_check():
    """Readiness check: verify Qdrant connectivity and required env."""
    problems = []
    # OpenAI key present
    if not os.getenv("OPENAI_API_KEY"):
        problems.append("OPENAI_API_KEY missing")
    # Qdrant connectivity
    q = check_qdrant_ready()
    if not q.get("ok"):
        problems.append(f"Qdrant not ready: {q.get('error')}")
    return {
        "ready": len(problems) == 0,
        "problems": problems,
        "timestamp": time.time(),
    }
