# rag/query.py

import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def ask_question(query: str, k: int = 4) -> str:
    """
    Loads Chroma vector store and uses RAG to answer the query.
    """
    print(f" Asking: {query}")

    # Load vectorstore
    embedding = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory="rag/chroma_db", embedding_function=embedding)

    # Build retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": k})

    # Set up GPT model
    llm = ChatOpenAI(model="gpt-4", temperature=0.5)

    # RAG chain: Retriever → LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa_chain.invoke(query)
    answer = result["result"]

    print("🧠 Answer generated:")
    return answer

if __name__ == "__main__":
    user_q = input("Ask a LayerZero question: ")
    response = ask_question(user_q)
    print(response)
