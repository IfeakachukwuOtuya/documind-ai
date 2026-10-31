# DocuMind AI

A Retrieval-Augmented Generation (RAG) assistant that answers questions from your documents, with citations.
Built step by step, adding production practices one module at a time.

## Run it (no AWS needed)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m documind.cli index
python -m documind.cli ask "How many days of annual leave do I get after 5 years?"
```

## Run it with real AWS Bedrock models

1. In the AWS console, open **Amazon Bedrock > Model access** in your region and enable **Titan Text Embeddings V2** and a **Claude** model.
2. Sign in locally: `aws configure` or `aws sso login`.
3. Set the mode and model, then rebuild the index (Bedrock vectors differ from offline ones):

```bash
export DOCUMIND_MODE=bedrock
export AWS_REGION=eu-west-2
export DOCUMIND_LLM_ID="<model ID from the Bedrock console>"
python -m documind.cli index
python -m documind.cli ask "How many days of annual leave do I get after 5 years?"
```

## Project layout

| File | Job |
|---|---|
| `documind/config.py` | Every setting in one place |
| `documind/ingest.py` | Load documents and cut them into chunks |
| `documind/embed.py` | Turn text into vectors (Titan, or offline stand-in) |
| `documind/store.py` | FAISS vector index: save, load, search |
| `documind/generate.py` | Prompt and answer generation (Claude, or offline stand-in) |
| `documind/pipeline.py` | Orchestration: runs the steps in order |
| `documind/cli.py` | Command line entry point |

## Roadmap

0 Baseline · 1 Configuration management · 2 Standards · 3 Evaluation · 4 Hybrid search and reranking ·
5 Guardrails · 6 Security · 7 Red teaming · 8 Secure CI/CD · 9 Governance · 10 Agentic security
