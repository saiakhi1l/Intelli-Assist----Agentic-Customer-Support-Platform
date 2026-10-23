# IntelliAssist — Agentic Customer Support

Production-oriented starter aligned with the resume: LangGraph orchestration, RAG over product documentation using FAISS + OpenAI embeddings, GPT-powered support responses, ticket escalation, FastAPI, Redis session memory, PostgreSQL ticket persistence, Docker, CI, and offline/online evaluation hooks.

**This is a runnable baseline, not proof of a production deployment or measured performance.** Configure secrets, load approved docs, test, and deploy in your environment before claiming production results.

## Run locally
1. Python 3.11+
2. `python -m venv .venv` and activate it.
3. `pip install -e ".[dev]"`
4. Copy `.env.example` to `.env`, set `GROQ_API_KEY` for chat and `OPENAI_API_KEY` for embeddings.
5. Add `.md` or `.txt` documents under `data/knowledge/`.
6. `python -m intelli_assist.ingest`
7. `uvicorn intelli_assist.api:app --reload`
8. API docs: `http://127.0.0.1:8000/docs`
9. `pytest` and `python -m evals.run_eval`

For local-only ticket/session state set `DATABASE_ENABLED=false`, `REDIS_ENABLED=false`. Groq handles chat generation; OpenAI is still used for embeddings in this version.

## API
`POST /chat`: `{"session_id":"s-1","message":"How do I reset my password?","customer_id":"c-1"}`
`POST /tickets`, `GET /tickets/{ticket_id}`, `GET /health`, `GET /metrics`.

## Design
Client → FastAPI → LangGraph → retrieval → classification → grounded response → deterministic policy gate → answer or ticket escalation. Redis stores bounded conversation history; PostgreSQL persists tickets. Every chat response includes online deterministic evaluation checks.

## Production hardening before public launch
Authentication/authorization, tenant isolation, rate limiting, TLS, PII redaction, secrets manager, Redis TLS/auth, database migrations, provider timeout/circuit breaker, load tests, human escalation integration, security review, retention policy, and alerting are still deployment tasks. Do not expose this starter publicly without them.

## Evaluation
Offline retrieval hit@k and retrieval latency are provided. Add a human-labelled held-out set and measure groundedness, answer correctness, citation precision, abstention, escalation precision/recall, p50/p95 latency, and cost per request. Set release thresholds from measured baselines; do not invent accuracy or latency claims.


## Groq configuration
This variant uses Groq for chat completions (`GROQ_API_KEY`, `GROQ_CHAT_MODEL`) and OpenAI embeddings for FAISS indexing (`OPENAI_API_KEY`). Groq chat and embedding are separate provider capabilities; changing the chat model does not replace the embedding model. If you want zero OpenAI dependency, switch `retrieval.py` to a local Hugging Face embedding model and re-index the knowledge base with the same embedding model used at query time.
