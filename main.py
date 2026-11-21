import argparse
from pathlib import Path

from openai import APIError

from advanced_rag import build_rag, retrieve
from generator import generate_answer


DOCUMENT_DIR = Path(__file__).resolve().parent / "Documents"


def main():
    parser = argparse.ArgumentParser(
        description="Ask questions about the SMB and Enterprise process documents."
    )
    parser.parse_args()

    documents = sorted(DOCUMENT_DIR.glob("*.docx"))
    if not documents:
        raise FileNotFoundError(
            f"No .docx documents found in {DOCUMENT_DIR}"
        )

    print("\n  WORKING PROCESS KNOWLEDGE ASSISTANT")
    print("  -----------------------------------")
    print("  Sources:")
    for document in documents:
        print(f"    - {document.stem}")

    status = build_rag(documents)
    if status["indexed"]:
        print(f"\n  Indexed {status['indexed']} document(s) into {status['chunks']} chunks.")
    if status["cached"]:
        print(f"  Reused the existing index for {status['cached']} unchanged document(s).")

    sources = status["sources"]
    print("\n  Ask about the SMB or Enterprise process. Type 'exit' to quit.")

    while True:
        query = input("\nYou: ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue

        try:
            results = retrieve(query, sources=sources)
            if not results:
                print("\nAssistant: I couldn't find relevant information in these documents.")
                continue
            answer = generate_answer(query, results)
        except APIError as exc:
            print(f"\nAssistant: Local model request failed: {exc}")
            continue

        print("\nAssistant:")
        print(answer)

        print("\nSources:")
        for index, result in enumerate(results, start=1):
            print(
                f"  [{index}] {result['source']} > {result['section']} "
                f"(chunk {result['chunk_id']})"
            )


if __name__ == "__main__":
    main()


