
import logging
import secrets
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from intelli_assist.config import settings
from intelli_assist.graph import SupportGraph
from intelli_assist.retrieval import KnowledgeRetriever
from intelli_assist.schemas import ChatRequest, ChatResponse
from intelli_assist.storage import SQLiteStore
from intelli_assist.storage_postgres import PostgresStore
from intelli_assist.ticket_service import TicketService

logger = logging.getLogger(__name__)

store = None
graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store, graph

    store = None
    graph = None

    try:
        # Use Neon PostgreSQL when DATABASE_URL is configured.
        # Otherwise, use SQLite for local development.
        if settings.storage_backend == "postgres":
            logger.info("Initializing PostgreSQL storage.")
            store = PostgresStore(settings.database_url)
        else:
            logger.info("Initializing SQLite storage.")
            store = SQLiteStore(settings.sqlite_path)

        # Configure the support graph when the Groq API key is available.
        if settings.groq_api_key:
            retriever = KnowledgeRetriever()
            retriever.initialize()

            ticket_service = TicketService(store)

            graph = SupportGraph(
                retriever=retriever,
                ticket_service=ticket_service,
            )
            logger.info("Support graph initialized successfully.")
        else:
            logger.warning(
                "GROQ_API_KEY is not configured; support graph is unavailable."
            )

        yield

    except Exception:
        logger.exception("Application startup failed.")
        raise

    finally:
        if store is not None and hasattr(store, "close"):
            store.close()

        store = None
        graph = None


app = FastAPI(
    title="IntelliAssist API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


def require_auth(
    authorization: str | None = Header(default=None),
):
    if not settings.api_auth_enabled:
        return {"sub": "local-development-user"}

    if not settings.api_bearer_token:
        raise HTTPException(
            status_code=500,
            detail="Authentication is not configured.",
        )

    expected = f"Bearer {settings.api_bearer_token}"

    if not authorization or not secrets.compare_digest(
        authorization,
        expected,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication.",
        )

    # Replace this simple development identity with a validated
    # JWT/OIDC principal before production use.
    return {"sub": "authenticated-user"}


@app.get("/health/live")
async def live():
    return {"status": "alive"}


@app.get("/health/ready")
async def ready():
    if store is None:
        raise HTTPException(
            status_code=503,
            detail="Storage is not ready.",
        )

    if graph is None:
        raise HTTPException(
            status_code=503,
            detail="Support graph is not configured.",
        )

    return {"status": "ready"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    principal: dict = Depends(require_auth),
):
    if graph is None or store is None:
        raise HTTPException(
            status_code=503,
            detail="Support service is not ready.",
        )

    # Use the authenticated identity, not a client-supplied customer ID.
    customer_id = principal["sub"]

    try:
        # Retrieve existing conversation context.
        conversation = store.get_conversation(
            customer_id=customer_id,
            session_id=request.session_id,
        )

        # Execute the support workflow.
        result = await graph.run(
            message=request.message,
            customer_id=customer_id,
            session_id=request.session_id,
            history=conversation["history"],
            summary=conversation["summary"],
            facts=conversation["facts"],
        )

        # Append the current interaction to conversation history.
        history = conversation["history"]

        history.extend(
            [
                {
                    "role": "user",
                    "content": request.message,
                },
                {
                    "role": "assistant",
                    "content": result.get("answer", ""),
                },
            ]
        )

        # Keep only the configured number of recent messages.
        max_messages = settings.max_history_turns * 2

        if max_messages > 0:
            history = history[-max_messages:]
        else:
            history = []

        # Persist conversation history.
        saved=store.save_conversation(
            customer_id=customer_id,
            session_id=request.session_id,
            history=history,
            summary=conversation["summary"],
            facts=conversation["facts"],
        )
        print("DEBUG customer_id:", customer_id)
        print("DEBUG session_id:", request.session_id)
        print("DEBUG saved conversation:", saved)

        # Return the structured API response.
        return ChatResponse(
            request_id=result.get("request_id", str(uuid4())),
            session_id=request.session_id,
            answer=result.get("answer", ""),
            intent=result.get("intent", "general"),
            priority=result.get("priority", "low"),
            escalated=result.get("escalated", False),
            escalation_reason=result.get("escalation_reason"),
            ticket_id=result.get("ticket_id"),
            citations=result.get("citations", []),
            evaluation=result.get("evaluation", {}),
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Chat request failed")

        raise HTTPException(
            status_code=500,
            detail="An internal support-service error occurred.",
        )
