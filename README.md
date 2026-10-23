# IntelliAssist — Agentic Customer Support Platform

An AI-powered customer support platform that combines **RAG, LangGraph, FastAPI, and Groq** to deliver context-aware responses, retrieve relevant product documentation, classify customer intent and priority, and escalate complex or sensitive requests for human support.

## Key Features

- **Agentic Workflow Orchestration:** Uses LangGraph to coordinate customer support workflows.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant information from product documentation using FAISS and OpenAI embeddings.
- **AI-Powered Responses:** Uses Groq-hosted language models to generate context-aware customer support answers.
- **Intent and Priority Classification:** Identifies customer intent and determines ticket priority.
- **Intelligent Ticket Escalation:** Routes complex or security-sensitive requests for human review.
- **Conversation Memory:** Supports session-based conversation history using Redis.
- **Ticket Management:** Persists support tickets using PostgreSQL.
- **REST API:** Provides endpoints through FastAPI for chat, ticket operations, health checks, and metrics.
- **Evaluation Framework:** Includes retrieval evaluation, latency measurements, and deterministic response checks.
- **Docker Support:** Supports containerized development and deployment workflows.

## Technology Stack

| Component | Technologies |
|---|---|
| Programming Language | Python |
| LLM Orchestration | LangChain, LangGraph |
| LLM Provider | Groq |
| Embeddings | OpenAI Embeddings |
| Vector Search | FAISS |
| Backend API | FastAPI |
| Session Memory | Redis |
| Ticket Persistence | PostgreSQL |
| Frontend | Next.js, React, TypeScript |
| Testing | Pytest |
| Deployment | Docker, CI/CD |

## Architecture

The platform follows an orchestrated customer support workflow:

1. **Customer Query:** Receives a support request through the frontend or API.
2. **Workflow Orchestration:** LangGraph manages the processing steps.
3. **Knowledge Retrieval:** Searches product documentation using FAISS and embeddings.
4. **Intent and Priority Classification:** Determines the request category and urgency.
5. **Response Generation:** Uses Groq to generate a grounded answer from the retrieved context.
6. **Policy Validation:** Applies deterministic checks to evaluate the response and identify sensitive requests.
7. **Ticket Escalation:** Routes requests requiring human intervention to the ticket workflow.
8. **State and Persistence:** Maintains conversation history and stores ticket information.

## Project Structure

```text
intelli_assist_groq/
├── intelli_assist/
│   ├── api.py
│   └── ...
├── data/
│   └── knowledge/
├── evals/
│   └── run_eval.py
├── tests/
├── intelliassist-frontend/
├── .env.example
├── .gitignore
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js and npm
- Groq API key
- OpenAI API key for embeddings

Redis and PostgreSQL are needed when their corresponding persistence features are enabled.

### 1. Clone the Repository

```bash
git clone https://github.com/saiakhi1l/Intelli-Assist----Agentic-Customer-Support-Platform.git
cd Intelli-Assist----Agentic-Customer-Support-Platform
```

### 2. Set Up the Python Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Configure the environment variables in a local `.env` file using `.env.example` as a reference. Add your own API keys and service configuration.

### 3. Prepare the Knowledge Base

Place approved Markdown or text documents in:

```text
data/knowledge/
```

Build the retrieval index:

```bash
python -m intelli_assist.ingest
```

### 4. Start the Backend

```bash
uvicorn intelli_assist.api:app --reload
```

The API documentation is available at:

http://127.0.0.1:8000/docs

### 5. Start the Frontend

Open a second terminal:

```bash
cd intelliassist-frontend
npm install
npm run dev
```

Open the frontend at:

http://localhost:3000

Configure `NEXT_PUBLIC_API_BASE_URL` to point to the backend URL when running outside the local development environment.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/chat` | Process a customer support message |
| POST | `/tickets` | Create a support ticket |
| GET | `/tickets/{ticket_id}` | Retrieve ticket details |
| GET | `/health` | Check API health |
| GET | `/metrics` | Access application metrics |

### Example Chat Request

```json
{
  "session_id": "s-1",
  "message": "How do I reset my password?",
  "customer_id": "c-1"
}
```

## Testing and Evaluation

Run the test suite:

```bash
pytest
```

Run the evaluation workflow:

```bash
python -m evals.run_eval
```

The evaluation workflow includes retrieval hit-at-k and retrieval latency measurements, along with deterministic response checks.

## Environment Configuration

Use `.env.example` to identify the required configuration variables. Keep actual API keys, database credentials, and other secrets in local environment files or your deployment provider's environment settings. Do not commit secret values to GitHub.

## Future Enhancements

- Authentication and role-based access control
- Multi-tenant customer support
- Advanced RAG evaluation and reranking
- Human-agent dashboard and escalation integrations
- Observability, tracing, and alerting
- Rate limiting and additional security controls
- Automated deployment pipelines

---

**IntelliAssist — Intelligent, context-aware, and workflow-driven customer support.**