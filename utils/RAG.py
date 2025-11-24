import json
import os
import faiss
import numpy as np
from utils.text_processing import get_chunks, embed_batch_ollama


class RAG:
    def __init__(
        self,
        client,
        folder="documents",
        batch_size=10,
        index_path="rag/faiss.index",
        chunks_path="rag/faiss_chunks.json",
    ):
        self.client = client
        self.folder = folder
        self.batch_size = batch_size
        self.index_path = index_path
        self.chunks_path = chunks_path

        # Load chunked data from cache if available; otherwise build and persist
        self.all_chunks, self.chunk_sources = self._load_or_prepare_chunks()

        # Build or load FAISS index
        self.index = self._load_or_build_index()

    def _load_or_prepare_chunks(self):
        """
        Load chunk text and sources from disk if available; otherwise build them
        from documents and persist for future runs.
        """
        if os.path.exists(self.chunks_path):
            try:
                with open(self.chunks_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data["all_chunks"], data["chunk_sources"]
            except Exception:
                # Fall back to rebuilding if cached chunks cannot be loaded
                pass

        all_chunks, chunk_sources = get_chunks(self.folder)
        self._save_chunks(all_chunks, chunk_sources)
        return all_chunks, chunk_sources

    def _save_chunks(self, all_chunks, chunk_sources):
        directory = os.path.dirname(self.chunks_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.chunks_path, "w", encoding="utf-8") as f:
            json.dump(
                {"all_chunks": all_chunks, "chunk_sources": chunk_sources},
                f,
                ensure_ascii=False,
            )

    def _load_or_build_index(self):
        """
        Try loading a persisted FAISS index; if unavailable or out of date,
        rebuild and save a fresh one.
        """
        if os.path.exists(self.index_path):
            try:
                index = faiss.read_index(self.index_path)

                # If the number of embeddings matches our current chunks, reuse the index
                if index.ntotal == len(self.all_chunks):
                    return index
            except Exception:
                # Fall back to rebuilding the index if anything goes wrong while loading
                pass

        index = self._build_index()
        self._save_index(index)
        return index

    def _save_index(self, index):
        directory = os.path.dirname(self.index_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        faiss.write_index(index, self.index_path)

    # Build FAISS index from all chunk embeddings
    def _build_index(self):
        vectors = []

        # Embed in batches (faster, avoids token overuse)
        for i in range(0, len(self.all_chunks), self.batch_size):
            batch = self.all_chunks[i:i + self.batch_size]
            vectors.append(embed_batch_ollama(batch))

        embeddings = np.vstack(vectors)

        # Store embeddings for retrieval
        self.embeddings = embeddings

        # Create FAISS index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        return index

    # Retrives nearest chunks
    def retrieve(self, query, k=3):
        q_vec = embed_batch_ollama([query])

        distances, idxs = self.index.search(q_vec, k)

        results = []
        for idx in idxs[0]:
            results.append({
                "chunk": self.all_chunks[idx],
                "source": self.chunk_sources[idx]
            })
        return results
