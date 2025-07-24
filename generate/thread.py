# generate/thread.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rag.query import ask_question
from langchain_openai import ChatOpenAI

def structure_thread_with_llm(context: str, template: str) -> str:
    """
    Uses OpenAI LLM to structure the thread by filling the template with a hook, body, and CTA extracted from the context.
    """
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
    """
    Takes RAG output and turns it into a tweet thread using a template retrieved from the RAG system.
    """
    # Retrieve the thread template from RAG
    template = ask_question("Provide the thread template for a Twitter thread", k=1)
    # Retrieve the context/content for the topic
    context = ask_question(topic)
    # Use LLM to structure the thread
    thread_text = structure_thread_with_llm(context, template)
    return thread_text

if __name__ == "__main__":
    topic = input("Enter a topic: ")
    result = generate_thread(topic)
    print(result)
