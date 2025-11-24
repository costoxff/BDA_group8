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


def rag_answer_with_memory(question, rag, user_id, memory, model="llama3"):
    """
    Answer a question using RAG with conversation history
    
    Args:
        question: User's current question
        rag: RAG instance for document retrieval
        user_id: User identifier for conversation history
        memory: ConversationMemory instance
        model: LLM model to use
        
    Returns:
        Answer string
    """
    # Retrieve relevant documents from RAG
    retrieved = rag.retrieve(question)
    document_context = "\n\n---\n\n".join([r["chunk"] for r in retrieved])
    
    # Retrieve conversation history
    conversation_history = memory.format_history_for_prompt(user_id)
    
    # Build enhanced prompt with conversation history and document context
    prompt = f"""You are a helpful AI assistant with access to both document knowledge and conversation history.

{conversation_history}
INSTRUCTIONS:
1. Use the conversation history above to maintain context and continuity, but only if there is relevant history.
2. Use the document context below as your primary knowledge source
3. If the question relates to something discussed earlier, acknowledge it
4. Be conversational and natural while staying accurate to the documents.
5. Do not explicitly mention the use of documents in your answers, unless it makes sense for the question.
6. Be concise, unless asked otherwise.

DOCUMENT CONTEXT:
{document_context}

CURRENT QUESTION FROM USER:
{question}

YOUR RESPONSE:
"""
    
    # Get answer from LLM
    answer = ollama_chat(prompt, model=model)
    
    # Store this exchange in conversation history
    memory.add_exchange(user_id, question, answer)
    
    return answer


if __name__ == "__main__":
    from conversation_memory import ConversationMemory
    
    print("Building RAG index...")

    # RAG loads all documents, chunks them, embeds them (via Ollama), and builds FAISS
    rag = RAG(
        client=None,
        folder="documents",
        batch_size=5
    )

    print("Index built.")
    print("")
    
    # Initialize conversation memory
    memory = ConversationMemory(storage_dir="conversation_history", max_history=10)
    
    # Use default user_id for now (until user functionality is implemented)
    user_id = "user"

    while True:
        # Example query
        question = input("Question (Q to quit): ")
        if question.upper() == 'Q':
            print("Quit LLM.")
            break

        print("")

        # Use the new function with memory
        answer = rag_answer_with_memory(question, rag, user_id, memory, model="llama3")

        print("ANSWER:")
        print(answer)
        print("")
        
        # Show conversation count
        count = memory.get_conversation_count(user_id)
        print(f"Total conversations for {user_id}: {count}")