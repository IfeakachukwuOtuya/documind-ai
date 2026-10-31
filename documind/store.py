"""
STEP 3 of indexing: store vectors in a FAISS index so we can search them fast.

FAISS compares the question's vector with every chunk's vector and returns the
closest ones. We save the chunk text alongside so we can show it and cite it.
"""

import json
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from .ingest import Chunk


class VectorStore:
    def __init__(self, dim: int):
        # Inner product on normalised vectors = cosine similarity (1.0 = identical meaning).
        self.index: faiss.Index = faiss.IndexFlatIP(dim)
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[Chunk, float]]:
        scores, ids = self.index.search(query_vector.reshape(1, -1), k)
        return [(self.chunks[i], float(s)) for i, s in zip(ids[0], scores[0], strict=True) if i != -1]

    def save(self, index_dir: str) -> None:
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, f"{index_dir}/faiss.index")
        Path(f"{index_dir}/chunks.json").write_text(
            json.dumps([asdict(c) for c in self.chunks], indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, index_dir: str) -> "VectorStore":
        index = faiss.read_index(f"{index_dir}/faiss.index")
        store = cls(index.d)
        store.index = index
        data = json.loads(Path(f"{index_dir}/chunks.json").read_text(encoding="utf-8"))
        store.chunks = [Chunk(**c) for c in data]
        return store
