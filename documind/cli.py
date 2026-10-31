
"""
Command line entry point.
  python -m documind.cli index
  python -m documind.cli ask "How many days of annual leave do I get?"
"""
import argparse

from .config import settings
from .pipeline import DocuMind


def main() -> None:
    parser = argparse.ArgumentParser(prog="documind")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("index", help="Build the search index from data/docs")
    ask = sub.add_parser("ask", help="Ask a question")
    ask.add_argument("question")
    args = parser.parse_args()

    app = DocuMind(settings)
    if args.command == "index":
        count = app.build_index()
        print(f"Indexed {count} chunks (mode: {settings.mode}).")
    else:
        answer = app.ask(args.question)
        print(answer.text)
        print("\nRetrieved:")
        for s in answer.sources:
            print(f"  {s['score']:.3f}  {s['chunk_id']}")


if __name__ == "__main__":
    main()