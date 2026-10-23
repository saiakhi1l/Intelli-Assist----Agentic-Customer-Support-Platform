
from langchain_core.messages import HumanMessage

from intelli_assist.schemas import ConversationFact, MemorySnapshot


def _message_text(message: dict) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    return str(content)


class ContextManager:
    def __init__(self, max_history_turns: int = 12):
        self.max_history_turns = max_history_turns

    def build_snapshot(
        self,
        history: list[dict],
        summary: str = "",
        facts: list[dict] | None = None,
    ) -> MemorySnapshot:
        recent = history[-self.max_history_turns * 2:]

        normalized_facts = []
        for item in facts or []:
            try:
                normalized_facts.append(
                    ConversationFact.model_validate(item)
                )
            except Exception:
                continue

        return MemorySnapshot(
            history=[
                {
                    "role": str(item.get("role", "user")),
                    "content": _message_text(item),
                }
                for item in recent
            ],
            summary=summary or "",
            facts=normalized_facts,
        )

    def render_context(
        self,
        snapshot: MemorySnapshot,
        max_chars: int = 18000,
    ) -> str:
        sections = []

        if snapshot.summary:
            sections.append(
                "PREVIOUS CONVERSATION SUMMARY:\n"
                + snapshot.summary
            )

        if snapshot.facts:
            fact_lines = [
                f"- {fact.key}: {fact.value} "
                f"(source: {fact.source})"
                for fact in snapshot.facts
            ]
            sections.append(
                "KNOWN CONVERSATION FACTS:\n"
                + "\n".join(fact_lines)
            )

        if snapshot.history:
            lines = []
            for message in snapshot.history:
                role = message["role"].upper()
                lines.append(
                    f"{role}: {message['content']}"
                )

            sections.append(
                "RECENT CONVERSATION:\n"
                + "\n".join(lines)
            )

        rendered = "\n\n".join(sections)
        return rendered[-max_chars:]

    async def update_summary(
        self,
        llm,
        previous_summary: str,
        older_messages: list[dict],
    ) -> str:
        if not older_messages:
            return previous_summary

        transcript = "\n".join(
            f"{item.get('role', 'user')}: "
            f"{_message_text(item)}"
            for item in older_messages
        )

        prompt = f"""
Update the persistent customer-support conversation summary.

Preserve:
- User-stated facts and corrections
- The unresolved customer issue
- Actions already attempted
- Advice already given
- Relevant decisions and outcomes

Do not invent facts.
Do not treat assistant assumptions as confirmed user facts.
Do not store passwords, API keys, payment credentials, or secrets.
Keep the summary concise.

Previous summary:
{previous_summary or "(none)"}

New messages:
{transcript}

Return only the updated summary.
"""

        result = await llm.ainvoke(
            [HumanMessage(content=prompt)]
        )
        return str(result.content).strip()
