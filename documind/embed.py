
"""
STEP 2 of indexing (and step 1 of answering): turn text into vectors.

A vector is a list of numbers that represents meaning. Texts with similar
meaning get similar vectors, which is what makes semantic search work:
"holiday entitlement" lands close to "annual leave".
"""
import hashlib
import json
import re

import numpy as np


class BedrockEmbedder:
    """Real embeddings from Amazon Titan on Bedrock."""

    def __init__(self, settings):
        import boto3
        self.client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
        self.model_id = settings.embedding_model_id
        self.dim = settings.embedding_dimensions

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            body = json.dumps({"inputText": text, "dimensions": self.dim, "normalize": True})
            response = self.client.invoke_model(modelId=self.model_id, body=body)
            vectors.append(json.loads(response["body"].read())["embedding"])
        return np.array(vectors, dtype="float32")


class OfflineEmbedder:
    """
    A free stand-in for learning and tests. It hashes words into a vector, so
    it matches on shared WORDS, not meaning. Good enough to run the pipeline
    without AWS; use Bedrock for real semantic search.
    """

    def __init__(self, settings, dim: int = 512):
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype="float32")
        for row, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dim
                vectors[row, bucket] += 1.0
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-9)


def get_embedder(settings):
    return BedrockEmbedder(settings) if settings.mode == "bedrock" else OfflineEmbedder(settings)