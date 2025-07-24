# rag/ingest.py

import os
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

def embed_documents(source_folder="data/docs", pdf_folder="data/LayerZero_primitives", template_folder="data/thread_templates"):
    """
    Loads all .txt or .md files from the data/docs folder,
    all .pdf files from the data/LayerZero_primitives folder,
    and all .md files from the data/thread_templates folder,
    splits them into chunks, embeds them using OpenAI, and stores them in Chroma.
    """
    print("📥 Loading documents...")
    all_docs = []

    # Ingest .txt and .md files from source_folder
    for filename in os.listdir(source_folder):
        if filename.endswith(".txt") or filename.endswith(".md"):
            path = os.path.join(source_folder, filename)
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            all_docs.extend(docs)

    # Ingest .pdf files from pdf_folder
    if os.path.exists(pdf_folder):
        for filename in os.listdir(pdf_folder):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, filename)
                loader = PyMuPDFLoader(pdf_path)
                docs = loader.load()
                all_docs.extend(docs)

    # Ingest .md template files from template_folder
    if os.path.exists(template_folder):
        for filename in os.listdir(template_folder):
            if filename.endswith(".md"):
                template_path = os.path.join(template_folder, filename)
                loader = TextLoader(template_path, encoding="utf-8")
                docs = loader.load()
                all_docs.extend(docs)

    print(f"🔍 {len(all_docs)} documents loaded.")
    
    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    split_docs = text_splitter.split_documents(all_docs)
    print(f"✂️ Split into {len(split_docs)} chunks.")

    # Create embeddings
    embeddings = OpenAIEmbeddings()

    # Store in Chroma vector database
    vectorstore = Chroma.from_documents(split_docs, embeddings, persist_directory="rag/chroma_db")

    print("Embeddings saved to chroma_db.")

if __name__ == "__main__":
    embed_documents()
