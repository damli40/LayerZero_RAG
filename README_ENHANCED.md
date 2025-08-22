# Enhanced Omnichain Assistant

A production-ready RAG system for LayerZero ecosystem knowledge with guardrails, retrieval optimizations, and multiple client interfaces (Web UI + Telegram).

## Features

### Core Architecture
- Ingestion → Split (markdown-aware + recursive) → Embeddings → Vector DB (Qdrant) + Metadata DB (SQLite)
- Orchestrator (FastAPI) + Clients (Web UI, Telegram bot)

### Retrieval & Quality
- Embeddings: OpenAI `text-embedding-3-large` (3072 dims)
- Structured chunking: Markdown header-aware + recursive splitter (~1200 chars, 200 overlap)
- Query expansion: Domain glossary (e.g., "lz" → "LayerZero") and multi‑variant queries
- MMR retrieval: Diversified candidates with higher `fetch_k`
- Neighbor context: Includes ±1 adjacent chunks for continuity
- Reranker (optional): Cross‑encoder reranking is currently DISABLED by default to reduce RAM in prod
- Clarifying fallback: Low confidence yields a short clarifying question instead of an error

### Guardrails & Safety
- Confidence threshold (default: 0.5; can override via `MIN_CONFIDENCE_THRESHOLD`)
- Clarifying fallback on low confidence (consumer UI hides confidence/sources)
- Prompt classification, tool restrictions, rate limiting, content safety checks, response sanitization

### Analytics & Monitoring
- SQLite metadata database for query tracking
- Usage analytics (query counts, timing, confidence)
- Health and readiness endpoints

## Quick Start

### 1) Install
```bash
pip install -r requirements.txt
```

### 2) Configure environment
Create a `.env` with:
```env
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-key
QDRANT_COLLECTION_NAME=layerzero-rag
OPENAI_API_KEY=your-openai-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
# Optional
MIN_CONFIDENCE_THRESHOLD=0.5
# Reranker is disabled in code by default; to enable later use env control
# RERANK_ENABLED=true
```

### 3) Ingest data
```bash
python rag/ingest.py
```

### 4) Run services
```bash
# Web UI
uvicorn app.main:app --reload
# Telegram bot
python bot/bot.py
```

## Structure
```
primer_omnichain_assistant/
├── app/                # FastAPI web app (UI hides confidence/sources)
├── bot/                # Telegram bot (confidence/sources hidden)
├── rag/
│   ├── ingest.py       # Ingestion with markdown-aware splitting + metadata
│   ├── query.py        # Retrieval (MMR, glossary, clarifier)
│   ├── rerank.py       # Cross-encoder reranker (optional/disabled by default)
│   ├── guardrails.py   # Guardrails and validation
│   ├── metadata_db.py  # SQLite logging/analytics
│   └── utils/
└── generate/           # Thread generation
```

## Configuration Notes

### Embeddings & Chunking
- Model: `text-embedding-3-large` (3072-d)
- Split: markdown headers → recursive chunks (~1200 chars, 200 overlap)

### Reranking (optional)
- Disabled by default to avoid large downloads/RAM in prod.
- To enable later: use a small model like `cross-encoder/ms-marco-MiniLM-L-6-v2` and restore env control in `is_rerank_enabled()`.
- Cross-encoder scores are sigmoid-mapped to [0,1].

### Guardrails
- `min_confidence_threshold` default 0.5; `MIN_CONFIDENCE_THRESHOLD` can override.
- On low confidence, system returns a clarifying question instead of an error.

## Usage

### Web
- Visit `http://localhost:8000`
- Ask questions; answers omit confidence/sources in UI
- Generate threads; output also omits confidence/sources

### Telegram
```bash
python bot/bot.py
# /thread <topic>
```

### API
```python
from rag.query import query_rag
result = query_rag("What is DVN?", user_id="u1", client_type="api")
print(result["response"])  # text answer
```

## Troubleshooting
- Qdrant connectivity: check `QDRANT_URL` and `check_qdrant_ready()`
- DNS errors on localhost vs container: ensure correct host and port
- Reranker downloads/memory: keep disabled or use a smaller model and persistent cache

## Notes on Production (Render)
- Use `.dockerignore` to keep image small; avoid baking large `data/` into images
- Consider a persistent disk and set `HF_HOME` if enabling reranker to cache models
- Set `RERANK_ENABLED=false` (or keep code-disabled) for low-RAM instances

---
Enhanced Omnichain Assistant — pragmatic RAG with guardrails and resilient retrieval for LayerZero. 