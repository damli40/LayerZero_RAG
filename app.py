# app.py

from rag.query import ask_question
from generate.thread import generate_thread

def run():
    print("\n🎙 Welcome to the Omnichain Thread Generator\n")

    query = input("🤔 What LayerZero topic do you want to write about?\n> ")

    print("\n🔍 Getting context with RAG...")
    context = ask_question(query)

    print("\n✍️ Generating thread...\n")
    thread = generate_thread(context)

    print("🧵 Here's your thread:\n")
    print(thread)

    # Optional: save it or offer to post
    save = input("\n💾 Save this thread to file? (y/n): ").lower()
    if save == "y":
        with open("generated_thread.txt", "w", encoding="utf-8") as f:
            f.write(thread)
        print("✅ Saved as generated_thread.txt")

if __name__ == "__main__":
    run()
