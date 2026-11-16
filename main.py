"""CLI REPL for the NovaCell support assistant. Type 'quit' to exit."""
from __future__ import annotations

import sys

from chain import stream_answer


def _print_sources(docs) -> None:
    print("\nSources:")
    for d in docs:
        label = f"  - [{d.metadata.get('source')} · {d.metadata.get('source_id')}]"
        print(label)


def main() -> None:
    print("NovaCell Support Assistant (CLI). Type 'quit' to exit.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            return

        try:
            token_stream, docs = stream_answer(question)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return

        print("\nAssistant: ", end="", flush=True)
        for token in token_stream:
            print(token, end="", flush=True)
        print()
        _print_sources(docs)


if __name__ == "__main__":
    main()
