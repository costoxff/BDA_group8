import glob
import numpy as np
import requests

import markdown
from bs4 import BeautifulSoup
from pathlib import Path


def load_text_files(folder="documents"):
    txt_files = glob.glob(f"{folder}/*.txt")
    md_files = glob.glob(f"{folder}/*.md")

    all_files =  txt_files + md_files

    docs = []

    for path in all_files:
        file_ext = Path(path).suffix.lower()

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if file_ext == ".md":
            content = markdown_to_text(content)
        
        docs.append((path, content))
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


def markdown_to_text(markdown_content):
    html = markdown.markdown(
        markdown_content,
        extensions=[
            'extra', 
            'codehilite',
            'toc',
            'nl2br'
        ]
    )
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup(['script', 'style']):
        tag.decompose()
    
    text = soup.get_text(separator='\n', strip=True)
    
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    return text