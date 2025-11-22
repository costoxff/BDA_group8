import faiss
import numpy as np
from text_processing import get_chunks, embed_batch_ollama


class RAG:
    def __init__(self, client, folder="documents", batch_size=10):
        self.client = client
        self.folder = folder
        self.batch_size = batch_size

        # Load and chunk documents
        self.all_chunks, self.chunk_sources = get_chunks(folder)

        # Build FAISS index
        self.index = self._build_index()


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
