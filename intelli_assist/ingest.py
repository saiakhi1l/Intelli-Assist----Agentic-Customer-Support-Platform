
from pathlib import Path

from langchain_core.documents import Document
from .config import get_settings
from .retrieval import KnowledgeRetriever


def load_documents(folder):
    docs = []

    for path in Path(folder).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            content = path.read_text(encoding="utf-8").strip()

            if content:
                docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": path.name,
                            "source_id": str(path.relative_to(folder)),
                        },
                    )
                )

    return docs


def main():
    settings = get_settings()

    docs = load_documents(settings.knowledge_dir)

    if not docs:
        raise RuntimeError(
            f"No .md/.txt files found in {settings.knowledge_dir}"
        )

    KnowledgeRetriever(settings).index_documents(docs)

    print(f"Indexed {len(docs)} documents.")


if __name__ == "__main__":
    main()
