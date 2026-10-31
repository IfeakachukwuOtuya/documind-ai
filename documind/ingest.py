"""
STEP 1 of indexing: load documents and cut them into chunks.

WHY CHUNK: a model can't read 500 pages per question, and search works best on
small, focused pieces. Each chunk keeps a record of which file it came from,
so answers can cite their source.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    chunk_id: str  # e.g. "annual_leave_policy.md#2"
    source: str  # file name, used for citations
    text: str


def load_documents(docs_dir: str) -> list[tuple[str, str]]:
    """Return (file_name, full_text) for every supported file in the folder."""
    docs = []
    for path in sorted(Path(docs_dir).glob("*")):
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            docs.append((path.name, path.read_text(encoding="utf-8")))
        elif suffix == ".pdf":
            from pypdf import PdfReader

            pages = [page.extract_text() or "" for page in PdfReader(path).pages]
            docs.append((path.name, "\n\n".join(pages)))
    return docs


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """
    Pack whole paragraphs into chunks of up to `size` characters.
    The last `overlap` characters of each chunk are repeated at the start of the
    next, so a sentence that spans a boundary is still findable.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if current and len(current) + len(para) + 2 > size:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = tail[tail.find(" ") + 1 :] if " " in tail else tail  # start on a whole word
        current = f"{current}\n\n{para}" if current else para

        # A single very long paragraph still has to be split.
        while len(current) > size:
            chunks.append(current[:size])
            current = current[size - overlap :]

    if current:
        chunks.append(current)
    return chunks


def build_chunks(docs_dir: str, size: int, overlap: int) -> list[Chunk]:
    chunks = []
    for name, text in load_documents(docs_dir):
        for i, piece in enumerate(chunk_text(text, size, overlap)):
            chunks.append(Chunk(chunk_id=f"{name}#{i}", source=name, text=piece))
    return chunks
