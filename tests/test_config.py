"""Configuration must reject bad values and fingerprint changes reliably."""

import pytest
from pydantic import ValidationError

from documind.config import Settings, load_settings


def make(**changes) -> Settings:
    values = load_settings("dev").model_dump()
    values.update(changes)
    return Settings(**values)


def test_dev_settings_load():
    s = load_settings("dev")
    assert s.environment == "dev"
    assert s.mode == "offline"


def test_prod_layer_overrides_only_what_it_lists():
    dev, prod = load_settings("dev"), load_settings("prod")
    assert prod.mode == "bedrock"
    assert prod.chunk_size == dev.chunk_size  # inherited from default.yaml


@pytest.mark.parametrize("field, bad_value", [("top_k", 0), ("top_k", 50), ("temperature", 2.0), ("mode", "bedrok")])
def test_out_of_range_values_are_rejected(field, bad_value):
    with pytest.raises(ValidationError):
        make(**{field: bad_value})


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValidationError, match="chunk_overlap"):
        make(chunk_size=400, chunk_overlap=400)


def test_unknown_setting_is_rejected():
    with pytest.raises(ValidationError):
        make(**{"top-k": 3})


def test_settings_cannot_change_at_runtime():
    s = load_settings("dev")
    with pytest.raises(ValidationError):
        s.top_k = 9


def test_fingerprint_changes_when_an_answer_setting_changes():
    assert make(top_k=4).fingerprint() != make(top_k=5).fingerprint()


def test_fingerprint_ignores_settings_that_do_not_affect_answers():
    assert make(docs_dir="a").fingerprint() == make(docs_dir="b").fingerprint()
