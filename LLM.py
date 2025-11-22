import requests

from RAG import RAG
from ollama_client import safe_post, CHAT_URL

def ollama_chat(prompt, model="llama3"):
    r = safe_post(
        CHAT_URL,
        {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = r.json()

    # DEBUG: Model didn’t respond with chat message
    if "message" not in data:
        raise ValueError(
            f"Ollama did not return a chat message.\n"
            f"Model: {model}\n"
            f"Prompt length: {len(prompt)} chars\n"
            f"Response:\n{data}\n\n"
            f"Try running:\n    ollama pull {model}"
        )

    return data["message"]["content"]


def rag_answer(question, rag, model="llama3"):
    retrieved = rag.retrieve(question)

    context = "\n\n---\n\n".join([r["chunk"] for r in retrieved])

    prompt = f"""
Use ONLY the following context to answer.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    return ollama_chat(prompt, model=model)


if __name__ == "__main__":
    print("Building RAG index...")

    # RAG loads all documents, chunks them, embeds them (via Ollama), and builds FAISS
    rag = RAG(
        client=None,
        folder="documents",
        batch_size=5
    )

    print("Index built.")
    print("")

    # Example query
    question = "What does the third document talk about?"

    print(f":{question}")
    print("")

    answer = rag_answer(question, rag, model="llama3")

    print("ANSWER:")
    print(answer)