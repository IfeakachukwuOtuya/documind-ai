"""
ORCHESTRATION: the code that runs the steps in the right order.

Two flows:
  build_index()  - run once (or when documents change): load -> chunk -> embed -> store
  ask()          - run per question: embed question -> retrieve -> generate -> answer

The [MODULE n] comments mark exactly where each later module plugs in.
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .embed import get_embedder
from .generate import get_generator
from .ingest import build_chunks
from .store import VectorStore


@dataclass
class Answer:
    question: str
    text: str
    sources: list[dict] = field(default_factory=list)  # what was retrieved, with scores
    config_version: str = ""      # which config file version produced this answer
    config_fingerprint: str = ""  # hash of every answer-affecting setting


class IndexMismatchError(RuntimeError):
    """The saved index was built with different settings from the ones running now."""


class DocuMind:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedder = get_embedder(settings)
        self.generator = get_generator(settings)
        self.store: VectorStore | None = None

    # ---------------- INDEXING FLOW ----------------
    def build_index(self) -> int:
        chunks = build_chunks(self.settings.docs_dir, self.settings.chunk_size,
                              self.settings.chunk_overlap)
        # [MODULE 6 - Security] tag each chunk with who is allowed to see it.
        vectors = self.embedder.embed([c.text for c in chunks])
        self.store = VectorStore(vectors.shape[1])
        self.store.add(chunks, vectors)
        # [MODULE 4 - Hybrid search] also build a keyword (BM25) index here.
        self.store.save(self.settings.index_dir)
        self._write_manifest(len(chunks))
        return len(chunks)

    def _write_manifest(self, chunk_count: int) -> None:
        """Record exactly what this index was built with, next to the index itself."""
        manifest = {
            "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "config_version": self.settings.config_version,
            "config_fingerprint": self.settings.fingerprint(),
            "chunk_count": chunk_count,
            "signature": self.settings.index_signature(),
        }
        path = Path(self.settings.index_dir) / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _check_manifest(self) -> None:
        """Refuse to answer from an index built with different embedding or chunk settings."""
        path = Path(self.settings.index_dir) / "manifest.json"
        if not path.exists():
            raise IndexMismatchError("No manifest found. Rebuild the index: python -m documind.cli index")
        built_with = json.loads(path.read_text(encoding="utf-8"))["signature"]
        running_with = self.settings.index_signature()
        differences = {k: (built_with.get(k), v) for k, v in running_with.items() if built_with.get(k) != v}
        if differences:
            details = ", ".join(f"{k}: index={old!r} config={new!r}" for k, (old, new) in differences.items())
            raise IndexMismatchError(
                f"Index does not match current config ({details}). "
                "Rebuild it: python -m documind.cli index"
            )

    # ---------------- ANSWERING FLOW ----------------
    def ask(self, question: str) -> Answer:
        if self.store is None:
            self._check_manifest()
            self.store = VectorStore.load(self.settings.index_dir)

        # [MODULE 5 - Guardrails] check the INPUT: PII, off-topic, injection attempts.

        query_vector = self.embedder.embed([question])[0]
        retrieved = self.store.search(query_vector, self.settings.top_k)
        # [MODULE 4 - Hybrid search] combine vector + keyword results, then rerank.
        # [MODULE 6 - Security] drop chunks this user isn't allowed to see.

        text = self.generator.generate(question, retrieved)

        # [MODULE 5 - Guardrails] check the OUTPUT: grounded? cited? safe?
        # [MODULE 9 - Governance] write an audit log entry (question, sources, answer, config version).

        sources = [{"chunk_id": c.chunk_id, "source": c.source, "score": round(s, 3)}
                   for c, s in retrieved]
        return Answer(question=question, text=text, sources=sources,
                      config_version=self.settings.config_version,
                      config_fingerprint=self.settings.fingerprint())