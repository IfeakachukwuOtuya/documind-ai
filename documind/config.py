
"""
All DocuMind settings in one place.

WHY ONE PLACE: every setting below changes the answers the system gives.
Keeping them together means you always know what the system is running with.

[MODULE 1 - Configuration management] will turn this into a versioned YAML
file with separate dev/prod settings.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # "offline" runs everything locally with no AWS cost (for learning/testing).
    # "bedrock" uses real AWS Bedrock models.
    mode: str = os.getenv("DOCUMIND_MODE", "offline")
    aws_region: str = os.getenv("AWS_REGION", "eu-west-2")  # London

    # Embedding model: turns text into a list of numbers (a vector).
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    embedding_dimensions: int = 1024

    # Generation model: writes the answer.
    generation_model_id: str = os.getenv(
        "DOCUMIND_LLM_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
    )

    # Chunking: how documents are cut into pieces before indexing.
    chunk_size: int = 400      # max characters per chunk
    chunk_overlap: int = 80    # characters repeated between chunks

    # Retrieval: how many chunks to pass to the model.
    top_k: int = 4

    # Generation behaviour.
    temperature: float = 0.0   # 0 = most consistent, least "creative"
    max_tokens: int = 500

    # Folders.
    docs_dir: str = "data/docs"
    index_dir: str = "index"


settings = Settings()