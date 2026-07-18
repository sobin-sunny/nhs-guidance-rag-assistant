"""
COMMAND-LINE INTERFACE
======================

The quickest way to test the assistant.

    python app/ask.py "How do I claim for prescription prepayment?"

Or run it with no question for an interactive prompt where you can keep asking.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.rag_engine import RagEngine  # noqa: E402


def show(result):
    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(result["answer"])
    print("\n" + "-" * 70)
    print("SOURCES USED (this is what makes the answer checkable)")
    print("-" * 70)
    for i, doc in enumerate(result["sources"], 1):
        src = doc.metadata.get("source_file", "?")
        page = doc.metadata.get("page", "?")
        snippet = doc.page_content[:160].replace("\n", " ")
        print(f"  {i}. {src} (page {page}): {snippet}...")
    print()


def main():
    print("Loading the assistant (this takes a few seconds the first time)...")
    engine = RagEngine()
    if not engine.llm_available:
        print("Note: local model not detected - running in retrieval-only mode.")

    question = " ".join(sys.argv[1:]).strip()
    if question:
        show(engine.answer(question))
        return

    print("\nAsk a question (or press Enter on an empty line to quit).")
    while True:
        try:
            q = input("\nYour question > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        show(engine.answer(q))


if __name__ == "__main__":
    main()
