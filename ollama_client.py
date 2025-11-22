# ollama_client.py
import os
import time
import requests


# -------------------------------------------
# CONFIGURATION (supports env variables)
# -------------------------------------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

CHAT_URL = f"{OLLAMA_HOST}/api/chat"
EMBED_URL = f"{OLLAMA_HOST}/api/embeddings"


# -------------------------------------------
# HELPER: Check if Ollama server is running
# -------------------------------------------
def wait_for_ollama(timeout=5):
    """Wait until Ollama is reachable. Returns True if OK, False otherwise."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(OLLAMA_HOST, timeout=0.5)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
    return False


# -------------------------------------------
# SAFE POST with automatic detection and error message
# -------------------------------------------
def safe_post(url, json):
    if not wait_for_ollama():
        raise ConnectionError(
            f"❌ Could not connect to Ollama at {OLLAMA_HOST}\n"
            f"➡️ Start the server by running the command:\n\n"
            f"    ollama serve\n\n"
            f"Or specify a custom host with:\n"
            f"    set OLLAMA_HOST=http://localhost:11435\n"
        )

    try:
        return requests.post(url, json=json)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to communicate with Ollama: {e}")
