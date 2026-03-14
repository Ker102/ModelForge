# gemini.md — ModelForge Dev Tracker

## Current Task
Session 2026-03-14 (evening) — Agent execution fix + persistence + observability

## What Changed (Session 2026-03-14 Evening)

### 🔴→✅ Agent Tool Execution Fix
- **Root cause found via LangSmith**: `MiddlewareError: System message should be the first one`
- `lib/ai/agents.ts` `createRAGMiddleware()` — was prepending a `SystemMessage` before the existing messages array, violating LangGraph's message ordering constraint
- **Fix**: RAG context now appended to the existing system message's content instead of creating a new one

### LangSmith Observability ✅
- `LANGSMITH_TRACING=true` already configured in `.env` with valid API key
- LangChain auto-detects env vars — traces ARE flowing (5 runs visible, 33k tokens)
- Debug script `scripts/test/debug-langsmith.ts` confirmed working
- The failed LangSmith trace (`019cedfc-...`) contained the exact error that revealed the root cause

## Previous Changes (Session 2026-03-14)
- Studio Chat Persistence (localStorage), Auth Pages Teal Redesign, BETA Badge, Filesystem Reorganization

## Known Issues / Blockers
- ~~Agent tool execution: All steps show red X~~ **FIXED** — RAG middleware SystemMessage ordering
- **gcloud auth expiry**: Vertex AI OAuth tokens expire frequently

## Remaining Tasks
1. ~~Debug agent tool execution failure~~ ✅ Fixed
2. Push branch + PR for CodeRabbit review (ongoing)
3. DB-backed Studio session persistence (localStorage → Prisma/PostgreSQL)
4. Feature brainstorm P2/P3 implementation

## Branch
`feature/addon-tools-phase3`
