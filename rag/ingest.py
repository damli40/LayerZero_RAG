# rag/ingest.py

import os
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

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
            all_docs.extend(loader.load())

    # Load PDFs
    if os.path.exists(pdf_folder):
        for filename in os.listdir(pdf_folder):
            if filename.endswith(".pdf"):
                loader = PyMuPDFLoader(os.path.join(pdf_folder, filename))
                all_docs.extend(loader.load())

    # Load templates
    if os.path.exists(template_folder):
        for filename in os.listdir(template_folder):
            if filename.endswith(".md"):
                loader = TextLoader(os.path.join(template_folder, filename), encoding="utf-8")
                all_docs.extend(loader.load())

    print(f"🔍 Loaded {len(all_docs)} documents.")

    # Split text
    splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(all_docs)
    print(f"✂️ Split into {len(chunks)} chunks.")

    # Embeddings
    embeddings = OpenAIEmbeddings()

    # Qdrant Setup
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")

    client = QdrantClient(url=url, api_key=api_key)

    # Create collection if it doesn't exist
    if collection_name not in [c.name for c in client.get_collections().collections]:
        print("🛠️ Creating Qdrant collection...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    # Store in vectorstore
    vectorstore = Qdrant.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=url,
        api_key=api_key,
        collection_name=collection_name,
    )

    print("✅ Ingestion complete! Vectorstore uploaded to Qdrant.")

if __name__ == "__main__":
    embed_documents()
