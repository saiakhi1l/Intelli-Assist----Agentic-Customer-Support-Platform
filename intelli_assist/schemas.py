from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str = Field(min_length=1, max_length=200)
    customer_id: str = Field(min_length=1, max_length=200)


class Citation(BaseModel):
    source: str
    score: float | None = None


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    answer: str
    intent: str = "general"
    priority: str = "low"
    escalated: bool = False
    escalation_reason: str | None = None
    ticket_id: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    evaluation: dict[str, Any] = Field(default_factory=dict)



class RouteDecision(BaseModel):
    route: Literal[
        "memory",
        "rag",
        "hybrid",
        "clarify",
        "support_action",
        "out_of_scope",
    ]

    intent: str = "general"

    priority: Literal[
        "low",
        "medium",
        "high",
        "urgent",
    ] = "low"

    needs_history: bool = False
    needs_retrieval: bool = False

    clarification_question: str | None = None
    reason: str = ""



class ConversationFact(BaseModel):
    key: str
    value: str
    source: Literal["user", "assistant", "system"] = "user"
    turn_index: int = 0


class MemorySnapshot(BaseModel):
    summary: str = ""
    facts: list[ConversationFact] = Field(default_factory=list)
    history: list[dict[str, str]] = Field(default_factory=list)