import json, statistics, time
from pathlib import Path
from intelli_assist_old.config import get_settings
from intelli_assist_old.retrieval import KnowledgeRetriever

def main():
    settings=get_settings()
    cases=[json.loads(x) for x in Path("evals/dataset.jsonl").read_text().splitlines() if x.strip()]
    if not settings.openai_api_key: raise SystemExit("Set OPENAI_API_KEY.")
    retriever=KnowledgeRetriever(settings)
    if not retriever.store: raise SystemExit("Index missing. Run python -m intelli_assist.ingest.")
    hits=[]; latencies=[]
    for case in cases:
        t=time.perf_counter()
        docs=retriever.search(case["question"],k=settings.retrieval_k)
        latencies.append((time.perf_counter()-t)*1000)
        sources=[d.metadata.get("source") for d,score in docs if score>=settings.min_retrieval_score]
        expected=case["expected_source"]
        hit=(1 if expected in sources else 0) if expected else None
        if hit is not None: hits.append(hit)
        print(json.dumps({"id":case["id"],"retrieved_sources":sources,"expected_source":expected,
                          "hit":hit,"retrieval_latency_ms":round(latencies[-1],2)}))
    print(json.dumps({"cases":len(cases),"retrieval_hit_rate":sum(hits)/len(hits) if hits else None,
        "p50_retrieval_ms":statistics.median(latencies),"note":"Starter dataset only; not a production benchmark."},indent=2))

if __name__=="__main__": main()
