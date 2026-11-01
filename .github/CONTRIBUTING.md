
# Contributing to DocuMind

These are the team's working standards. They exist so that quality does not depend on who wrote the code.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Mac/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Before every pull request

```bash
python scripts/check.py
```

This runs formatting, linting (including security rules), type checking and tests. CI runs the same checks, and a pull request cannot be merged until they pass.

## Code standards

1. **Formatting is automatic.** Run `ruff format .`. Layout is never discussed in review.
2. **Understand a lint finding before changing it.** Fix the cause, or state the intent in code (for example `usedforsecurity=False`). If a rule must be ignored, use a `# noqa: <code>` on that line with a comment explaining why.
3. **Type hints on all functions.** `mypy documind` must pass.
4. **Every behaviour change has a test,** including at least one failure or edge case (empty input, bad config, missing file).
5. **Tests are offline and isolated.** No AWS calls, no network, temporary folders only. They must run in seconds.

## Configuration standards

1. Every setting that affects answers lives in `config/`, never hard-coded.
2. Changing an answer-affecting setting means bumping `config_version`.
3. Changing embedding or chunking settings means rebuilding the index; the manifest check enforces this.
4. **Never put secrets in config, code, tests or commit history.** AWS access comes from IAM roles or your local AWS login.

## RAG-specific standards

1. Answers must cite their sources. The prompt rules in `generate.py` are not changed without an evaluation run.
2. Retrieved document text is untrusted data, never instructions.
3. Permission filtering happens before generation, never after.

## Commits and pull requests

- Small commits that each do one thing, with a message saying what changed.
- Every change goes through a pull request using the template, and is reviewed by one other person.
- Never rewrite history on a shared branch.

## Code review: what reviewers look for

Automated checks handle style. Reviewers focus on:

- **Correctness:** does it do what the PR says? Are edge cases tested?
- **Security:** untrusted input, secrets, permissions, logging of personal data.
- **Answer quality:** could this change retrieval or answers? If so, was it evaluated?
- **Clarity:** could a new team member understand and safely change it?
