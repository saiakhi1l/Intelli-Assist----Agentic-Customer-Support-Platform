
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from intelli_assist.config import get_settings


class KnowledgeRetriever:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.settings.embedding_model
        )

        self.index_dir = Path(self.settings.faiss_index_dir)
        self.knowledge_dir = Path(self.settings.knowledge_dir)
        self.vectorstore = None

    def index_documents(self, documents):
        if not documents:
            raise ValueError("Cannot index an empty document list.")

        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Build a fresh index from all supplied documents.
        new_vectorstore = FAISS.from_documents(
            documents,
            self.embeddings,
        )

        # Save to a temporary directory first, preserving the old index
        # until the new index has been built successfully.
        temp_dir = self.index_dir.parent / f"{self.index_dir.name}_new"
        temp_dir.mkdir(parents=True, exist_ok=True)

        new_vectorstore.save_local(str(temp_dir))

        # Load the newly saved index to verify that it can be opened.
        verified_vectorstore = FAISS.load_local(
            str(temp_dir),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        # Keep the verified vectorstore active in this process.
        self.vectorstore = verified_vectorstore

        # Replace the old index files only after successful construction
        # and verification. Back up the old index before running ingestion.
        for filename in ("index.faiss", "index.pkl"):
            source = temp_dir / filename
            if not source.exists():
                raise RuntimeError(
                    f"Expected FAISS file was not created: {source}"
                )

        for filename in ("index.faiss", "index.pkl"):
            destination = self.index_dir / filename
            destination.write_bytes(
                (temp_dir / filename).read_bytes()
            )

        print(f"Successfully indexed {len(documents)} documents.")

    def initialize(self):
        index_file = self.index_dir / "index.faiss"

        if index_file.exists():
            self.vectorstore = FAISS.load_local(
                str(self.index_dir),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            return

        raise RuntimeError(
            "FAISS index not found. Run the ingestion script first."
        )

    def search(self, query: str, k: int | None = None) -> list[dict]:
        if self.vectorstore is None:
            raise RuntimeError(
                "Knowledge retriever has not been initialized."
            )

        results = self.vectorstore.similarity_search_with_score(
            query,
            k=k or self.settings.retrieval_k,
        )

        documents = []

        for document, distance in results:
            source = Path(
                document.metadata.get("source", "unknown")
            ).name

            documents.append({
                "content": document.page_content,
                "source": source,
                "distance": float(distance),
            })

        return documents
