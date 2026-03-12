# gemini.md — ModelForge Dev Tracker

## Current Task
LangChain v1 Migration & Agent Refactoring

## What Changed (Latest)
- **LangChain v1 Migration**: Upgraded entire LangChain stack to v1:
  - `langchain@^1.2.0`, `@langchain/core@^1.1.0`, `@langchain/google-genai@^2.1.0`
  - `@langchain/langgraph@^1.2.0`, `@langchain/anthropic@^1.3.0`, `langsmith@^0.5.0`
- **New Agent** (`lib/ai/agents.ts`):
  - LangChain v1 `createAgent` with middleware stack
  - 14 MCP tools wrapped as LangChain `tool()` with Zod schemas
  - Viewport screenshot middleware (auto-capture after `execute_code`)
  - RAG context middleware using `SystemMessage` injection
  - Session persistence via `MemorySaver` (thread_id = projectId)
- **New Executor** (`lib/orchestration/executor.ts`):
  - `PlanExecutor` wraps LangChain v1 agent, compatible interface for API routes
  - Passes plan context + projectId for session persistence
- **Legacy Preservation**:
  - `agents.legacy.ts` and `executor.legacy.ts` preserved as dead code
  - All legacy importers updated to reference `.legacy` modules
- **Type Fixes** for `@langchain/core` v1:
  - `BaseMessage` type casts updated for new API surface
  - Added `AgentStepScreenshot` to `AgentStreamEvent` union
  - Fixed `visualValidation.screenshot` property name

## Previous Changes
- Agent Iteration Behavior & Viewport Screenshot Observability
- Migrated 3 animation scripts to Blender 5.0+ Slotted Actions API
- Deep research: 64 sources from NotebookLM on Blender 5.0 animation API

## Next Steps
- Add LangSmith env vars (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`)
- Run full build (`npm run build`) to verify no runtime issues
- Test agent end-to-end in Blender
- Consider session persistence DB upgrade (MemorySaver → PostgreSQL)
