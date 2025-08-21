# rag/ingest.py

import os
import hashlib
from typing import List, Dict
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_core.documents import Document
from datetime import datetime

load_dotenv()

def embed_documents(
    source_folder="data/docs",
    pdf_folder="data/LayerZero_primitives",
    template_folder="data/thread_templates"
):
    print("📥 Loading documents...")
    all_docs: List[Document] = []

    def _stable_document_id(source_type: str, path: str) -> str:
        content = f"{source_type}:{os.path.abspath(path)}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _source_weight_for(source_type: str) -> float:
        if source_type == "pdf":
            return 1.1
        if source_type == "template":
            return 0.9
        return 1.0

    # Load txt and md files
    for filename in os.listdir(source_folder):
        if filename.endswith(".txt") or filename.endswith(".md"):
            file_path = os.path.join(source_folder, filename)
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                source_type = "text"
                document_id = _stable_document_id(source_type, file_path)
                doc.metadata.update({
                    "source": filename,
                    "path": file_path,
                    "source_type": source_type,
                    "ingestion_date": datetime.utcnow().isoformat(),
                    "source_weight": _source_weight_for(source_type),
                    # keep backward-compatible key expected by reranker
                    "doc_id": document_id,
                    # provide explicit stable id
                    "document_id": document_id,
                })
            all_docs.extend(docs)

    # Load PDFs
    if os.path.exists(pdf_folder):
        for filename in os.listdir(pdf_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(pdf_folder, filename)
                loader = PyMuPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    source_type = "pdf"
                    document_id = _stable_document_id(source_type, file_path)
                    doc.metadata.update({
                        "source": filename,
                        "path": file_path,
                        "source_type": source_type,
                        "ingestion_date": datetime.utcnow().isoformat(),
                        "source_weight": _source_weight_for(source_type),
                        "doc_id": document_id,
                        "document_id": document_id,
                    })
                all_docs.extend(docs)

    # Load templates
    if os.path.exists(template_folder):
        for filename in os.listdir(template_folder):
            if filename.endswith(".md"):
                file_path = os.path.join(template_folder, filename)
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
                for doc in docs:
                    source_type = "template"
                    document_id = _stable_document_id(source_type, file_path)
                    doc.metadata.update({
                        "source": filename,
                        "path": file_path,
                        "source_type": source_type,
                        "ingestion_date": datetime.utcnow().isoformat(),
                        "source_weight": _source_weight_for(source_type),
                        "doc_id": document_id,
                        "document_id": document_id,
                    })
                all_docs.extend(docs)

    print(f"🔍 Loaded {len(all_docs)} documents.")

    # First: structure-aware split for Markdown by headers
    structured_docs: List[Document] = []
    md_header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
            ("####", "h4"),
        ]
    )

    for doc in all_docs:
        source_type = doc.metadata.get("source_type", "text")
        source_name = doc.metadata.get("source", "")
        if source_type in {"text", "template"} and source_name.endswith(".md"):
            header_docs = md_header_splitter.split_text(doc.page_content)
            for hdoc in header_docs:
                new_meta: Dict = doc.metadata.copy()
                new_meta.update(hdoc.metadata or {})
                # Build section path and title
                section_keys = [key for key in ["h1", "h2", "h3", "h4"] if new_meta.get(key)]
                section_vals = [new_meta[key] for key in section_keys]
                section_path = " > ".join(section_vals) if section_vals else None
                title = new_meta.get("h1") or new_meta.get("title")
                if section_path:
                    new_meta["section_path"] = section_path
                if title:
                    new_meta["title"] = title
                structured_docs.append(
                    Document(page_content=hdoc.page_content, metadata=new_meta)
                )
        else:
            structured_docs.append(doc)

    print(f"🧱 Structured into {len(structured_docs)} sections (markdown-aware).")

    # Second: recursive character splitter to create embedding chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks: List[Document] = splitter.split_documents(structured_docs)

    # Assign chunk indices per stable document id
    per_doc_counters: Dict[str, int] = {}
    for chunk in chunks:
        document_id = chunk.metadata.get("document_id") or chunk.metadata.get("doc_id") or "unknown"
        per_doc_counters.setdefault(document_id, 0)
        idx = per_doc_counters[document_id]
        chunk.metadata["chunk_index"] = idx
        per_doc_counters[document_id] = idx + 1

    print(f"✂️ Split into {len(chunks)} chunks.")

    # Embeddings - Using text-embedding-3-large
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        dimensions=3072  # text-embedding-3-large uses 3072 dimensions
    )

    # Qdrant Setup
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    client = QdrantClient(url=url, api_key=api_key)

    # Create collection if it doesn't exist - updated for text-embedding-3-large
    if collection_name not in [c.name for c in client.get_collections().collections]:
        print("🛠️ Creating Qdrant collection...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),  # Updated for text-embedding-3-large
        )

    # Store in vectorstore
    try:
        print("🔄 Attempting to store documents in Qdrant...")
        vectorstore = Qdrant.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=url,
            api_key=api_key,
            collection_name=collection_name,
        )
        print("✅ Successfully stored documents in Qdrant!")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error during document storage: {error_msg}")
        
        if "dimensions" in error_msg:
            print("🔄 Existing collection has different dimensions. Recreating collection...")
            try:
                # Delete existing collection
                client.delete_collection(collection_name=collection_name)
                print("🗑️ Deleted existing collection")
                
                # Recreate collection with correct dimensions
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
                )
                print("🛠️ Recreated collection with correct dimensions")
                
                # Try again
                vectorstore = Qdrant.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    url=url,
                    api_key=api_key,
                    collection_name=collection_name,
                )
                print("✅ Successfully stored documents after collection recreation!")
            except Exception as recreate_error:
                print(f"❌ Failed to recreate collection: {recreate_error}")
                raise recreate_error
        elif "validation" in error_msg.lower() or "pydantic" in error_msg.lower():
            print("🔄 Qdrant client version compatibility issue detected. Trying with force_recreate...")
            try:
                vectorstore = Qdrant.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    url=url,
                    api_key=api_key,
                    collection_name=collection_name,
                    force_recreate=True,
                )
                print("✅ Successfully stored documents with force_recreate!")
            except Exception as force_error:
                print(f"❌ Failed with force_recreate: {force_error}")
                raise force_error
        else:
            print(f"❌ Unknown error: {error_msg}")
            raise e

    print("✅ Ingestion complete! Vectorstore uploaded to Qdrant.")

if __name__ == "__main__":
    embed_documents()
