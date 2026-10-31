"""
Configuration management: load, layer, validate and fingerprint settings.

Settings come from three layers. Later layers win:
  1. config/default.yaml            - development defaults, committed to Git
  2. config/<environment>.yaml      - e.g. prod.yaml, only the values that differ
  3. environment variables          - per-machine overrides (never secrets in files)

The environment is chosen with DOCUMIND_ENV (default: dev).
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

# Environment variables that may override a setting, and which setting they override.
ENV_OVERRIDES = {
    "DOCUMIND_MODE": "mode",
    "AWS_REGION": "aws_region",
    "DOCUMIND_LLM_ID": "generation_model_id",
}

# Settings that change the ANSWERS. Their hash is the config fingerprint.
ANSWER_FIELDS = ["mode", "embedding_model_id", "embedding_dimensions", "generation_model_id",
                 "temperature", "max_tokens", "chunk_size", "chunk_overlap", "top_k"]

# Settings baked into the INDEX. If any differ from the index's manifest, rebuild.
INDEX_FIELDS = ["mode", "embedding_model_id", "embedding_dimensions", "chunk_size", "chunk_overlap"]


class Settings(BaseModel):
    # frozen: no changes at runtime. extra="forbid": unknown keys (typos) are errors.
    model_config = ConfigDict(frozen=True, extra="forbid")

    config_version: str
    environment: str
    mode: Literal["offline", "bedrock"]
    aws_region: str
    embedding_model_id: str
    embedding_dimensions: Literal[256, 512, 1024]
    generation_model_id: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: int = Field(gt=0, le=4096)
    chunk_size: int = Field(ge=100, le=4000)
    chunk_overlap: int = Field(ge=0)
    top_k: int = Field(ge=1, le=20)
    docs_dir: str
    index_dir: str

    @model_validator(mode="after")
    def overlap_must_be_smaller_than_chunk(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be smaller than chunk_size ({self.chunk_size})"
            )
        return self

    def fingerprint(self) -> str:
        """A short ID that changes whenever any answer-affecting setting changes."""
        values = {name: getattr(self, name) for name in ANSWER_FIELDS}
        return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()[:12]

    def index_signature(self) -> dict:
        """The settings an index depends on. Saved with the index, checked when loading it."""
        return {name: getattr(self, name) for name in INDEX_FIELDS}


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_settings(environment: str | None = None) -> Settings:
    environment = environment or os.getenv("DOCUMIND_ENV", "dev")

    values = _read_yaml(CONFIG_DIR / "default.yaml")              # layer 1
    values.update(_read_yaml(CONFIG_DIR / f"{environment}.yaml"))  # layer 2
    for env_var, field_name in ENV_OVERRIDES.items():              # layer 3
        if os.getenv(env_var):
            values[field_name] = os.getenv(env_var)

    values["environment"] = environment
    return Settings(**values)  # validation happens here


settings = load_settings()