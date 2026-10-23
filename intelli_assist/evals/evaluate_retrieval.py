
import json
import sys
from pathlib import Path

# Project root: C:\projects\intelli_assist_groq
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from intelli_assist.retrieval import KnowledgeRetriever

DATASET_PATH = PROJECT_ROOT / "evals" / "dataset.jsonl"
K = 3


def load_dataset(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Evaluation dataset not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main():
    dataset = load_dataset(DATASET_PATH)

    retriever = KnowledgeRetriever()
    retriever.initialize()

    total = len(dataset)
    if total == 0:
        print("Evaluation dataset is empty.")
        return

    hits = 0
    precision_scores = []
    reciprocal_ranks = []

    print(f"Evaluating {total} questions with K={K}\n")

    for item in dataset:
        question = item["question"]
        expected_source = item.get("expected_source")
        relevant_sources = (
            {Path(expected_source).name}
            if expected_source
            else set(item.get("relevant_sources", []))
        )

        results = retriever.search(question, k=K)
        retrieved_sources = [result["source"] for result in results]

        relevant_positions = [
            rank
            for rank, source in enumerate(retrieved_sources, start=1)
            if source in relevant_sources
        ]

        hit = bool(relevant_positions)
        hits += int(hit)

        relevant_count = sum(
            source in relevant_sources for source in retrieved_sources
        )
        precision_scores.append(relevant_count / K)

        reciprocal_rank = (
            1 / relevant_positions[0] if relevant_positions else 0
        )
        reciprocal_ranks.append(reciprocal_rank)

        print(f"Question: {question}")
        print(f"Expected source: {expected_source or sorted(relevant_sources)}")
        print(f"Expected behavior: {item.get('expected_behavior', 'not specified')}")
        print(f"Retrieved sources: {retrieved_sources}")
        print(f"Distances: {[round(r['distance'], 4) for r in results]}")
        print(
            f"Hit@{K}: {int(hit)} | "
            f"Precision@{K}: {precision_scores[-1]:.3f} | "
            f"Reciprocal rank: {reciprocal_rank:.3f}\n"
        )

    print("===== RETRIEVAL EVALUATION SUMMARY =====")
    print(f"Questions evaluated: {total}")
    print(f"Hit Rate@{K}: {hits / total:.3f}")
    print(f"Mean Precision@{K}: {sum(precision_scores) / total:.3f}")
    print(f"MRR: {sum(reciprocal_ranks) / total:.3f}")


if __name__ == "__main__":
    main()
