
import {
  Bot,
  UserRound,
  ShieldAlert,
  FileText,
  TicketCheck,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatResponse } from "@/lib/types";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
  time: string;
};

function Priority({ value }: { value?: string | null }) {
  if (!value) return null;

  const v = value.toLowerCase();

  return <span className={`pill priority-${v}`}>{v}</span>;
}

// Remove empty source labels and internal citation markers.
function cleanAnswer(text: string) {
  return text
    .replace(/\s*\[SOURCE_\d+\]/gi, "")
    .replace(/\s*\[Source:\s*\]/gi, "")
    .replace(/\s*\[Source:[^\]]*\]/gi, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

// Reduce excessive blank lines while preserving Markdown paragraphs.
function compactMarkdown(text: string) {
  return text
    .replace(/\r\n/g, "\n")
    .replace(/\n[ \t]*\n(?:[ \t]*\n)+/g, "\n\n")
    .trim();
}

export default function ChatMessage({
  message,
}: {
  message: Message;
}) {
  const isUser = message.role === "user";
  const response = message.response;

  const answerText = isUser
    ? message.text
    : compactMarkdown(cleanAnswer(message.text));

  return (
    <article
      className={`message-row ${
        isUser ? "user-row" : "assistant-row"
      }`}
    >
      <div
        className={`avatar ${
          isUser ? "user-avatar" : "bot-avatar"
        }`}
      >
        {isUser ? (
          <UserRound size={17} />
        ) : (
          <Bot size={18} />
        )}
      </div>

      <div className="message-content">
        <div className="message-meta">
          <strong>{isUser ? "You" : "IntelliAssist"}</strong>
          <span>{message.time}</span>
        </div>

        <div
          className={`bubble ${
            isUser ? "user-bubble" : "assistant-bubble"
          }`}
        >
          {isUser ? (
            <p
              className="message-text"
              style={{ whiteSpace: "pre-wrap" }}
            >
              {answerText}
            </p>
          ) : (
            <div className="message-text markdown-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => (
                    <p className="compact-paragraph">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="compact-list">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="compact-list">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="compact-list-item">{children}</li>
                  ),
                }}
              >
                {answerText}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {response && (
          <>
            {(response.intent || response.priority) && (
              <div className="response-tags">
                {response.intent && (
                  <span className="pill intent-pill">
                    {response.intent.replaceAll("_", " ")}
                  </span>
                )}

                <Priority value={response.priority} />
              </div>
            )}

            {response.escalated && (
              <div className="notice escalation-notice">
                <ShieldAlert size={17} />

                <div>
                  <strong>Escalation indicated</strong>

                  <p>
                    {response.escalation_reason ||
                      "This conversation has been marked for support escalation."}
                  </p>

                  {response.ticket_id && (
                    <span className="ticket-number">
                      <TicketCheck size={14} />
                      Ticket: {response.ticket_id}
                    </span>
                  )}
                </div>
              </div>
            )}

            {response.citations &&
              response.citations.length > 0 && (
                <details className="sources-panel">
                  <summary>
                    <FileText size={15} />
                    Sources ({response.citations.length})
                  </summary>

                  <ul>
                    {response.citations.map((citation, index) => (
                      <li key={`${citation.source}-${index}`}>
                        <span>{citation.source}</span>

                        {typeof citation.score === "number" && (
                          <small>
                            Score: {citation.score.toFixed(3)}
                          </small>
                        )}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
          </>
        )}
      </div>
    </article>
  );
}

export type { Message };
