"""
Run every quality check the team agreed on, in one command:
    python scripts/check.py

The same checks run in CI on every pull request (Module 8), so if this passes
locally, the pipeline should pass too.
"""

import subprocess
import sys

CHECKS = [
    ("Formatting", ["ruff", "format", "--check", "."]),
    ("Lint and security rules", ["ruff", "check", "."]),
    ("Type checking", ["mypy", "documind"]),
    ("Tests", ["pytest", "-q"]),
]


def main() -> int:
    failed = []
    for name, command in CHECKS:
        print(f"\n=== {name}: {' '.join(command)} ===", flush=True)
        # Fixed commands, run through this project's Python, never built from user input.
        result = subprocess.run([sys.executable, "-m", *command], check=False)  # noqa: S603
        if result.returncode != 0:
            failed.append(name)

    print("\n" + "=" * 50)
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
