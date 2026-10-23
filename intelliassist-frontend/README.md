# IntelliAssist Frontend

A Next.js App Router frontend for the existing IntelliAssist FastAPI + LangGraph + Groq backend. Includes responsive chat, suggested prompts, loading/error states, returned intent/priority/escalation/ticket information, and citations.

## Prerequisites
- Node.js 20.9+ (recommended for Next.js 15)
- npm
- Existing IntelliAssist FastAPI backend

## Run locally (Windows CMD)
From this frontend directory:

```cmd
copy .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000. Ensure the Python backend is running on http://127.0.0.1:8000.

`.env.local` should contain:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The frontend sends `POST /chat` with `{ "message": "...", "session_id": "..." }` when a session ID is available. It expects the API to return an object with `answer` and optionally `session_id`, `intent`, `priority`, `escalated`, `escalation_reason`, `ticket_id`, and `citations: [{"source":"...","score":0.3}]`.

## Deploy frontend to Vercel
1. Push this frontend directory to a GitHub repository, or deploy the monorepo with Vercel's Root Directory set to `frontend`.
2. In Vercel project Settings → Environment Variables, set `NEXT_PUBLIC_API_BASE_URL` to your **public deployed backend HTTPS URL**, for example `https://your-api.example.com` (replace with your real backend URL).
3. Deploy/redeploy.

Do not set `NEXT_PUBLIC_API_BASE_URL` to `127.0.0.1` or `localhost` on Vercel; those addresses refer to the visitor's own machine. The FastAPI backend must be deployed and reachable publicly over HTTPS. Configure FastAPI CORS to allow your exact Vercel origin (for example `https://your-project.vercel.app`). Keep Groq/API secrets only on the backend, never in frontend environment variables.

## Important backend checks
- `POST /chat` must accept `message` and optionally `session_id`.
- It should return an `answer` field and the other response fields are optional.
- If backend session handling expects a different request schema, adjust `src/lib/api.ts` and `src/app/page.tsx` to match the actual schema.
- This UI only displays a ticket ID if the backend actually returns one; it does not create tickets on its own.

## Build check
```cmd
npm run build
```
