# Production Runbook

## Release gates
- Use a versioned, human-labelled held-out test set; 100–300 representative cases is a starting point, not a guarantee of statistical coverage.
- Measure Recall@k/MRR, answer correctness, groundedness, citation precision, abstention quality, escalation precision/recall, cost, and p50/p95 end-to-end latency.
- Test prompt injection in retrieved docs, PII requests, fraud, unknown policies, malformed input, and provider timeouts.
- Derive thresholds from measured baselines and business risk; don't present targets as measured outcomes.
- Enable auth, tenant isolation, rate limits, TLS, PII redaction, retention controls, and secrets management before public exposure.

## Online evaluation
Each answer runs deterministic checks for non-empty output, retrieval evidence, citation IDs, and escalation. Metrics are exported at `/metrics`. Expensive LLM-as-judge scoring should run asynchronously on sampled traces, with a versioned rubric and human review for low scores/disagreements. A judge score alone must not trigger irreversible actions.

## Incident response
1. Check `/health`, `/metrics`, structured logs, provider status and dependencies.
2. Separate retrieval, model, Redis and database latency.
3. Route uncertain answers to humans if hallucinations rise.
4. Use bounded retries, timeouts and circuit breakers for providers.
5. Roll back model/prompt/index versions if release gates regress.
