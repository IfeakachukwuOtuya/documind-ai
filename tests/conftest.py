"""Shared test setup: fixtures that every test file can use."""

import pytest

from documind.config import Settings, load_settings


@pytest.fixture
def settings(tmp_path) -> Settings:
    """Offline dev settings, but with the index written to a temporary folder."""
    values = load_settings("dev").model_dump()
    values.update(mode="offline", index_dir=str(tmp_path / "index"))
    return Settings(**values)
