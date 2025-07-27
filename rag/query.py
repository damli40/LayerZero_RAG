# rag/query_rag.py

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores.qdrant import Qdrant  # ✅ Corrected import
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

# Set up retriever
def get_relevant_documents(query: str, k: int = 4) -> list[Document]:
    embeddings = OpenAIEmbeddings()

    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    qdrant_vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=QDRANT_COLLECTION_NAME,
        embeddings=embeddings,
    )

    retriever = qdrant_vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)  # ✅ Correct method

# Format context into prompt
def build_metaprompt(question: str, docs: list[Document]) -> str:
    context = "\n\n".join([doc.page_content for doc in docs])
    return f"""
You are a knowledgeable assistant for the LayerZero ecosystem.
Use the following context to answer the user's question.
If the answer is not found in the context, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""

# Run the RAG query
def query_rag(question: str, k: int = 4) -> str:
    docs = get_relevant_documents(question, k=k)  # Pass k to retriever
    metaprompt = build_metaprompt(question, docs)

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(metaprompt)
    return response.content

# Example usage
if __name__ == "__main__":
    user_question = input("Ask a question: ")
    print("\n🧠 Answer:")
    print(query_rag(user_question))
