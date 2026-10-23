export type Citation = { source: string; score?: number | null };
export type ChatResponse = {
  request_id?: string;
  session_id?: string;
  answer: string;
  intent?: string | null;
  priority?: "low" | "medium" | "high" | "urgent" | string | null;
  escalated?: boolean;
  escalation_reason?: string | null;
  ticket_id?: string | null;
  citations?: Citation[] | null;
  evaluation?: Record<string, unknown> | null;
};
export type ChatRequest = { message: string; session_id?: string; customer_id?: string };
