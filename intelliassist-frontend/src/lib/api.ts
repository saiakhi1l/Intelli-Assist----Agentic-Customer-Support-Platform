import type { ChatRequest, ChatResponse } from "@/lib/types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45_000);
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const raw = await response.text();
    let data: unknown;
    try { data = raw ? JSON.parse(raw) : {}; } catch { data = { detail: raw }; }
    if (!response.ok) {
      const detail = typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail: unknown }).detail) : `Request failed (${response.status})`;
      throw new Error(detail);
    }
    if (typeof data !== "object" || data === null || !("answer" in data)) {
      throw new Error("The API response did not include an answer. Check the FastAPI /chat response schema.");
    }
    return data as ChatResponse;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw new Error("The request took too long. Please try again.");
    if (error instanceof TypeError) throw new Error(`Cannot reach the API at ${API_BASE_URL}. Check that FastAPI is running and CORS allows this frontend origin.`);
    throw error;
  } finally { clearTimeout(timeout); }
}
