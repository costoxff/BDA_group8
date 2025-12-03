
import os
from typing import Tuple

from LLM import ollama_chat


def summarize_user_knowledge(
    user_name: str,
    history_dir: str = "conversation_history",
    summary_dir: str = "knowledge_summaries",
    model: str = "llama3",
) -> Tuple[str, str]:

    history_path = os.path.join(history_dir, f"{user_name}.txt")

    if not os.path.exists(history_path):
        raise FileNotFoundError(
            f"No conversation history found for '{user_name}' at {history_path}"
        )

    with open(history_path, "r", encoding="utf-8") as f:
        history_text = f.read().strip()

    if not history_text:
        raise ValueError(f"Conversation history for '{user_name}' is empty.")

    # Can adjust if needed
    prompt = f"""Summarize what the user appears to know about Advanced Care Planning (ACP) based on the following conversation history.
Focus on facts/topics the user has asked about or been told. Avoid guessing at motivations or adding new facts.

CONVERSATION HISTORY:
{history_text}

SUMMARY:"""

    summary_text = ollama_chat(prompt, model=model).strip()

    os.makedirs(summary_dir, exist_ok=True)
    summary_path = os.path.join(summary_dir, f"{user_name}_knowledge.txt")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    return summary_text, summary_path   # Could also have it return nothing
