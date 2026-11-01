"""End-to-end tests of the whole pipeline, offline, so they are free and run anywhere."""

import pytest

from documind.config import Settings
from documind.pipeline import DocuMind, IndexMismatchError


def test_answers_cite_the_right_policy(settings):
    app = DocuMind(settings)
    app.build_index()
    answer = app.ask("How many days of annual leave after 5 years?")
    assert answer.sources[0]["source"] == "annual_leave_policy.md"
    assert "30 days" in answer.text
    assert "[source: annual_leave_policy.md]" in answer.text


def test_answers_are_stamped_with_the_config(settings):
    app = DocuMind(settings)
    app.build_index()
    answer = app.ask("What is the hotel limit in London?")
    assert answer.config_version == settings.config_version
    assert answer.config_fingerprint == settings.fingerprint()


def test_returns_top_k_sources(settings):
    app = DocuMind(settings)
    app.build_index()
    assert len(app.ask("expenses").sources) == settings.top_k


def test_refuses_an_index_built_with_different_chunking(settings):
    DocuMind(settings).build_index()
    changed = Settings(**{**settings.model_dump(), "chunk_size": 300})
    with pytest.raises(IndexMismatchError, match="chunk_size"):
        DocuMind(changed).ask("anything")


def test_refuses_an_index_without_a_manifest(settings):
    with pytest.raises(IndexMismatchError, match="No manifest"):
        DocuMind(settings).ask("anything")
