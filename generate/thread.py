# generate/thread.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.query import query_rag
from langchain_openai import ChatOpenAI

def structure_thread_with_llm(context: str, template: str) -> str:
    llm = ChatOpenAI(model="gpt-4", temperature=0.5)
    prompt = (
        f"Given the following context, extract a compelling hook, a main body, and a call to action (CTA). "
        f"Then fill the following template:\n\n"
        f"Template:\n{template}\n\n"
        f"Context:\n{context}\n\n"
        f"Return ONLY the filled template."
    )
    response = llm.invoke(prompt)
    return response.content.strip()

def generate_thread(topic: str) -> str:
    template = query_rag("thread template for a Twitter thread", k=1)
    context = query_rag(topic)
    thread_text = structure_thread_with_llm(context, template)
    return thread_text

if __name__ == "__main__":
    topic = input("Enter a topic: ")
    result = generate_thread(topic)
    print(result)
