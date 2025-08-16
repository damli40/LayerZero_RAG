# rag/ingest.py

import os
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
import uuid
from datetime import datetime

load_dotenv()

def embed_documents(
    source_folder="data/docs",
    pdf_folder="data/LayerZero_primitives",
    template_folder="data/thread_templates"
):
    print("📥 Loading documents...")
    all_docs = []

    # Load txt and md files
    for filename in os.listdir(source_folder):
        if filename.endswith(".txt") or filename.endswith(".md"):
            loader = TextLoader(os.path.join(source_folder, filename), encoding="utf-8")
            docs = loader.load()
            # Add metadata for source tracking
            for doc in docs:
                doc.metadata.update({
                    "source": filename,
                    "source_type": "text",
                    "ingestion_date": datetime.utcnow().isoformat(),
                    "doc_id": str(uuid.uuid4())
                })
            all_docs.extend(docs)

    # Load PDFs
    if os.path.exists(pdf_folder):
        for filename in os.listdir(pdf_folder):
            if filename.endswith(".pdf"):
                loader = PyMuPDFLoader(os.path.join(pdf_folder, filename))
                docs = loader.load()
                # Add metadata for source tracking
                for doc in docs:
                    doc.metadata.update({
                        "source": filename,
                        "source_type": "pdf",
                        "ingestion_date": datetime.utcnow().isoformat(),
                        "doc_id": str(uuid.uuid4())
                    })
                all_docs.extend(docs)

    # Load templates
    if os.path.exists(template_folder):
        for filename in os.listdir(template_folder):
            if filename.endswith(".md"):
                loader = TextLoader(os.path.join(template_folder, filename), encoding="utf-8")
                docs = loader.load()
                # Add metadata for source tracking
                for doc in docs:
                    doc.metadata.update({
                        "source": filename,
                        "source_type": "template",
                        "ingestion_date": datetime.utcnow().isoformat(),
                        "doc_id": str(uuid.uuid4())
                    })
                all_docs.extend(docs)

    print(f"🔍 Loaded {len(all_docs)} documents.")

    # Split text
    splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(all_docs)
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
