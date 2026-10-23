"use client";

import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import { Activity, ArrowUp, Bot, Check, ChevronDown, CircleHelp, Headphones, Menu, MessageSquare, Plus, ShieldCheck, Sparkles, Trash2, Wifi, X } from "lucide-react";
import ChatMessage, { type Message } from "@/components/ChatMessage";
import { sendChatMessage } from "@/lib/api";
import type { ChatResponse } from "@/lib/types";

const suggestions = [
  { title: "Refund policy", prompt: "What is your refund policy?" },
  { title: "Payment issue", prompt: "My payment failed but the money was deducted. What should I do?" },
  { title: "Order delivery", prompt: "My package is delayed. What should I do?" },
  { title: "Account security", prompt: "I think someone has accessed my account without permission." },
];
const makeWelcome = (): Message => ({
  id: "welcome",
  role: "assistant",
  text: "Hi! I’m IntelliAssist, your AI support assistant. I can help with account access, billing, orders, refunds, shipping, and more. What can I help you with today?",
  time: "",
});

function nowTime() {
  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  }).format(new Date());
}function makeId() { return typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`; }

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([makeWelcome()]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }); }, [messages, loading]);
  useEffect(() => {
  setMessages((prev) =>
    prev.map((message) =>
      message.id === "welcome" && !message.time
        ? { ...message, time: nowTime() }
        : message
    )
  );
}, []);

  async function submitMessage(text: string) {
    const message = text.trim();
    if (!message || loading) return;
    setError(""); setInput(""); setLoading(true);
    setMessages(prev => [...prev, { id: makeId(), role: "user", text: message, time: nowTime() }]);
    try {
      const payload = {
         message,
        session_id: sessionId || makeId(),
        customer_id: "customer_01",
      };
      const response: ChatResponse = await sendChatMessage(payload);
      if (response.session_id) setSessionId(response.session_id);
      setMessages(prev => [...prev, { id: makeId(), role: "assistant", text: response.answer, response, time: nowTime() }]);
    } catch (e) {
      const errorMessage =
  e instanceof Error
    ? e.message
    : typeof e === "string"
      ? e
      : JSON.stringify(e);

setError(errorMessage);
    } finally { setLoading(false); inputRef.current?.focus(); }
  }

  function onSubmit(e: FormEvent<HTMLFormElement>) { e.preventDefault(); void submitMessage(input); }
  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void submitMessage(input); } }
  function newChat() { setMessages([makeWelcome()]); setSessionId(""); setInput(""); setError(""); setSidebarOpen(false); inputRef.current?.focus(); }

  return (
    <main className="app-shell">
      {sidebarOpen && <button aria-label="Close navigation overlay" className="mobile-overlay" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand"><div className="brand-mark"><Sparkles size={21} /></div><div><strong>IntelliAssist</strong><span>AI SUPPORT PLATFORM</span></div><button className="icon-button sidebar-close" aria-label="Close menu" onClick={() => setSidebarOpen(false)}><X size={18} /></button></div>
        <button className="new-chat-button" onClick={newChat}><Plus size={17} /> New conversation <span>⌘ K</span></button>
        <div className="side-label">WORKSPACE</div>
        <button className="nav-item nav-active"><MessageSquare size={17} /> AI Support Chat <span className="nav-dot" /></button>
        <button className="nav-item" onClick={() => setError("Ticket dashboard is planned for a later iteration. Ticket information returned by the API appears in chat messages.")}><Activity size={17} /> Ticket activity <span className="soon-label">SOON</span></button>
        <button className="nav-item" onClick={() => setError("Help center management is planned for a later iteration. Ask the assistant about current support policies.")}><CircleHelp size={17} /> Help center <span className="soon-label">SOON</span></button>
        <div className="sidebar-spacer" />
        <div className="privacy-card"><div className="privacy-icon"><ShieldCheck size={17} /></div><div><strong>Support with care</strong><p>Never share passwords, OTPs, or full card details in chat.</p></div></div>
        <div className="profile"><div className="profile-avatar">IA</div><div className="profile-info"><strong>IntelliAssist Demo</strong><span>Customer support</span></div><ChevronDown size={16} className="profile-chevron" /></div>
      </aside>

      <section className="main-panel">
        <header className="topbar"><div className="topbar-left"><button className="icon-button mobile-menu" aria-label="Open menu" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div className="top-title"><span className="eyebrow">WORKSPACE / SUPPORT</span><h1>AI Support Chat</h1></div></div><div className="topbar-right"><div className="connection-status"><span className="status-dot" /><span>Assistant workspace</span></div><button className="icon-button top-help" aria-label="Help" onClick={() => setError("Ask a question below. For account security issues, never share passwords or verification codes.")}><CircleHelp size={19} /></button></div></header>

        <div className="chat-stage">
          <div className="conversation-heading"><div className="conversation-icon"><Headphones size={20} /></div><div><h2>How can we help?</h2><p>Get clear answers from your support knowledge base.</p></div><div className="online-badge"><span /> AI ONLINE</div></div>
          <div className="messages-scroll" ref={scrollRef}>
            {messages.map(message => <ChatMessage key={message.id} message={message} />)}
            {loading && <div className="message-row assistant-row"><div className="avatar bot-avatar"><Bot size={18} /></div><div className="message-content"><div className="message-meta"><strong>IntelliAssist</strong><span>Thinking…</span></div><div className="bubble assistant-bubble typing-bubble"><span /><span /><span /></div></div></div>}
            {messages.length === 1 && !loading && <div className="suggestions"><p>QUICK START</p><div className="suggestion-grid">{suggestions.map(s => <button key={s.title} className="suggestion-card" onClick={() => void submitMessage(s.prompt)}><span>{s.title}</span><ArrowUp size={15} className="suggestion-arrow" /><small>{s.prompt}</small></button>)}</div></div>}
            {error && <div className="error-banner" role="alert"><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError("")}><X size={16} /></button></div>}
          </div>
          <div className="composer-wrap"><form className="composer" onSubmit={onSubmit}><textarea ref={inputRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={onKeyDown} placeholder="Describe your issue or ask a question…" rows={1} maxLength={10000} disabled={loading} aria-label="Message IntelliAssist"/><div className="composer-footer"><div className="composer-hint"><Sparkles size={14} /><span>AI-generated responses may need verification</span></div><div className="composer-actions"><span className="char-count">{input.length}/10000</span><button type="submit" className="send-button" disabled={!input.trim() || loading} aria-label="Send message">{loading ? <span className="send-spinner" /> : <ArrowUp size={18} />}</button></div></div></form><p className="disclaimer"><Check size={12} /> Do not include passwords, OTPs, or full payment-card details.</p></div>
        </div>
        <footer className="app-footer"><span><Wifi size={13} /> IntelliAssist support environment</span><span>Built with LangGraph + Groq</span></footer>
      </section>
    </main>
  );
}
