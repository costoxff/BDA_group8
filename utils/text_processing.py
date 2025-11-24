import glob
import numpy as np
import requests


def load_text_files(folder="documents"):
    files = glob.glob(f"{folder}/*.txt")
    docs = []

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            docs.append((path, f.read()))
    return docs


# RAG needs chunks
def chunk_text(text, chunk_size=1500, overlap=200):
    chunks = []
    start = 0
    end = chunk_size

    while start < len(text):
        chunks.append(text[start:end])
        start = end - overlap
        end = start + chunk_size

    return chunks


def get_chunks(folder="documents"):
    docs = load_text_files(folder)

    all_chunks = []
    chunk_sources = []

    for path, text in docs:
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
        chunk_sources.extend([path] * len(chunks))

    return all_chunks, chunk_sources


def embed_ollama(texts, model="mxbai-embed-large"):
    vectors = []
    for t in texts:
        r = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": model, "prompt": t}
        )
        vectors.append(r.json()["embedding"])
    return np.array(vectors, dtype="float32")


"""
# Deprecated for now, kept in case we switch to OpenAI in the future
# client should be the OpenAI client
def embed_batch(client, texts):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    return np.array([item.embedding for item in response.data], dtype="float32")
"""

def embed_batch_ollama(texts, model="mxbai-embed-large"):
    return embed_ollama(texts, model)