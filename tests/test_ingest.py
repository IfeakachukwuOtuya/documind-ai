"""Chunking must respect size limits, keep overlap, and never lose text."""

from documind.ingest import build_chunks, chunk_text

TEXT = "\n\n".join(f"Paragraph {i}. " + "word " * 30 for i in range(10))


def test_no_chunk_exceeds_the_size_limit():
    assert all(len(c) <= 400 for c in chunk_text(TEXT, size=400, overlap=80))


def test_consecutive_chunks_overlap():
    chunks = chunk_text(TEXT, size=400, overlap=80)
    tail_words = chunks[0].split()[-3:]
    assert " ".join(tail_words) in chunks[1]


def test_the_end_of_the_document_is_never_lost():
    chunks = chunk_text(TEXT, size=400, overlap=80)
    assert chunks[-1].endswith(TEXT.split("\n\n")[-1].strip())


def test_a_single_huge_paragraph_is_still_split():
    chunks = chunk_text("x" * 1000, size=400, overlap=80)
    assert len(chunks) > 1
    assert all(len(c) <= 400 for c in chunks)


def test_empty_text_gives_no_chunks():
    assert chunk_text("", size=400, overlap=80) == []


def test_chunks_are_labelled_with_their_source(tmp_path):
    (tmp_path / "policy.md").write_text("Line one.\n\nLine two.", encoding="utf-8")
    (tmp_path / "ignored.docx").write_text("not supported", encoding="utf-8")
    chunks = build_chunks(str(tmp_path), size=400, overlap=80)
    assert [c.chunk_id for c in chunks] == ["policy.md#0"]
    assert chunks[0].source == "policy.md"
