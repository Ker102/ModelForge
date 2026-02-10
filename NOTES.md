# ModelForge Project Notes

## Current Status (2026-02-10)

### System Architecture
- **Next.js 16**: App Router, Turbopack dev server on port 3000
- **Gemini 2.5 Pro**: LLM via `@langchain/google-genai`, model configurable via `GEMINI_MODEL` env var (defaults to `gemini-2.5-pro`), maxOutputTokens 65,536
- **Blender 5.x**: Target version. MCP addon connects via TCP socket on port 9876 (`BLENDER_MCP_PORT`)
- **Together.ai Embeddings**: Model `Alibaba-NLP/gte-modernbert-base` (768 dims, 8192 token context). Previously used `m2-bert-80M-32k-retrieval` (retired from Together serverless)
- **Neon pgvector**: Vector store for RAG, 113 documents ingested from `data/blender-scripts/*.py`
- **Supabase Auth**: Full auth flow (NextAuth completely removed)
- **Electron Desktop**: `desktop/` directory, launches via `cd desktop && MODELFORGE_DESKTOP_ENV=development ./node_modules/.bin/electron .`
- **Stripe**: Free / Starter ($12/mo) / Pro ($29/mo) tiers

### Two-Phase Orchestration Architecture
1. **Planning Phase**: Gemini generates a JSON plan with step descriptions (no code yet)
2. **Code Generation Phase**: For each step, Gemini generates Python code with full Blender API context
3. **Execution**: Code sent to Blender via MCP `execute_code` tool (takes `{ code: string }` ONLY)
4. **Validation**: Auto-validate on MCP success via `isMcpSuccess()` helper
5. **Recovery**: On failure, `normalizeParameters()` strips `description` when `code` exists to prevent addon rejection

### Key Files (Architecture Reference)
- `lib/orchestration/chains.ts` — LangChain chains for planning + code generation
- `lib/orchestration/executor.ts` — `PlanExecutor.executePlan()` — runs steps via MCP
- `lib/orchestration/planner.ts` — Entry point for orchestration
- `lib/orchestration/prompts.ts` — `PLANNING_SYSTEM_PROMPT`, `CODE_GENERATION_PROMPT` (LangChain f-string format — literal `{` `}` MUST be `{{` `}}`)
- `lib/orchestration/prompts/blender-agent-system.md` — Detailed Blender agent system prompt
- `lib/orchestration/prompts/index.ts` — Loads blender-agent-system.md (uses `process.cwd()`, not `__dirname`)
- `lib/orchestration/tool-registry.ts` — MCP tool definitions with parameter schemas + allow flags
- `lib/orchestration/types.ts` — Orchestration-specific types (different `PlanStep` than chains.ts!)
- `lib/orchestration/plan-utils.ts` — `normalizeParameters()`, `isMcpSuccess()`
- `lib/ai/prompts.ts` — General AI system prompts (updated for Blender 5.x)
- `lib/ai/embeddings.ts` — Together.ai embedding functions (`embedText`, `EMBEDDING_DIMENSIONS`)
- `lib/ai/vectorStore.ts` — pgvector similarity search
- `lib/generation/client.ts` — Replicate client (lazy init via `getReplicate()`, graceful when no API key)
- `app/api/ai/chat/route.ts` — Main chat API route (~742 lines)
- `scripts/ingest-blender-docs.ts` — RAG ingestion script

### Blender 5.x API Notes (Critical for Code Generation)
- `material.use_nodes = True` — DEPRECATED, node trees created automatically
- `world.use_nodes` — DEPRECATED, same reason
- EEVEE engine ID is `BLENDER_EEVEE` (NOT `BLENDER_EEVEE_NEXT`)
- Principled BSDF inputs unchanged from 4.x naming (`Base Color`, `Metallic`, `Roughness`, etc.)
- All `data/blender-scripts/*.py` files + addon files already cleaned of deprecated calls

### Known Type Gotchas
- **Two `PlanStep` types exist**: `chains.ts` has `expected_outcome`, `orchestration/types.ts` has `expectedOutcome` + `stepNumber`. Route.ts uses `stepAny` cast pattern to bridge them.
- LangChain prompt templates use f-string parser: all literal `{` must be `{{`
- `__dirname` resolves wrong in Next.js builds — always use `process.cwd()` for file paths to source

### Environment Variables (Required)
```
DATABASE_URL          — Neon PostgreSQL connection (pooled)
DIRECT_URL            — Neon direct connection (for migrations)
GEMINI_API_KEY        — Google AI API key for Gemini
TOGETHER_API_KEY      — Together.ai API key for embeddings
BLENDER_MCP_HOST      — 127.0.0.1
BLENDER_MCP_PORT      — 9876
STRIPE_SECRET_KEY     — Stripe secret key
STRIPE_WEBHOOK_SECRET — Stripe webhook secret
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY — Stripe publishable key
STRIPE_*_PRICE_ID     — 4 Stripe price IDs (starter/pro × monthly/yearly)
NEXT_PUBLIC_SUPABASE_URL  — Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY — Supabase anon key
```
Optional: `GEMINI_MODEL` (defaults to `gemini-2.5-pro`), `REPLICATE_API_TOKEN` (for 3D gen, gracefully absent), `FIRECRAWL_API_KEY` (web research)

## Completed Milestones
- [x] Supabase Auth migration (removed NextAuth, @auth/prisma-adapter, bcryptjs)
- [x] Auto-provisioning of Prisma user records on first Supabase login
- [x] Stripe customer sync on auth (idempotent background task)
- [x] Electron app loads correctly from Next.js dev server (port 3000)
- [x] Middleware cleaned up (protects /dashboard and /generate)
- [x] Two-phase orchestration (planning JSON → per-step Python code gen)
- [x] MCP connection indicator probes actual addon (not just TCP)
- [x] Addon UI sync on File → New with `@persistent` load_post handler
- [x] Tool filtering — disabled tools (Sketchfab, PolyHaven) excluded from planner
- [x] Parameter schemas added to tool registry
- [x] 3 critical bugs fixed: recovery param leak, Blender API compat, code gen scope
- [x] All code/prompts updated 4.x → Blender 5.x
- [x] RAG re-ingested with new embedding model (113 docs)
- [x] Full TypeScript build passes clean (12 files fixed)
- [x] System prompts audited and improved

## Recent Git History (as of 2026-02-10)
```
b40c6c7 Fix TypeScript build errors across 12 files
e977261 Switch embedding model to gte-modernbert-base, fix ingestion script
4b17f6f Update all Blender API references to 5.x
4be553b fix: 3 critical bugs - recovery description leak, Blender 4.x API, code gen scope
ec721d4 Audit & upgrade system prompts, add missing tool, fix param name
12e2d41 fix: add parameter schemas to tool registry
4295f45 fix: filter disabled tools from planner
515b2d1 fix: revert CodeRabbit auto-validation change
d5c0f98 fix: sync addon UI with actual server state after File → New/Open
2634781 fix: address CodeRabbit review suggestions
f516848 feat: add Blender MCP connection indicator near prompt bar
```

## Outstanding Work
1. **Test end-to-end** — Connect to Blender 5.x via MCP and test full scene generation flow
2. **Iterate on orchestration quality** — Test various prompts, tune code gen reliability
3. **Viewport screenshots** — Integrate MCP viewport results into chat UI
4. **Deploy to production** — Vercel/DigitalOcean with production database
5. **Package Electron** — Auto-update, installers for Linux/Mac/Windows
6. **Add monitoring/tests** — MCP connection health, integration tests

## How to Start Development
```bash
# Terminal 1: Next.js dev server
cd /media/krist/CrucialX9/cursor-projects/projects/project02/BlenderAI
npm run dev

# Terminal 2: Electron app
cd desktop
MODELFORGE_DESKTOP_ENV=development ./node_modules/.bin/electron .

# Blender: Must be running with ModelForge addon enabled and connected (port 9876)
```

## How to Re-ingest RAG Embeddings
If `data/blender-scripts/*.py` files change:
```bash
npx tsx scripts/ingest-blender-docs.ts
```
Requires `TOGETHER_API_KEY` and `DATABASE_URL` in `.env`.

Refer to `blendermcpreadme.md` and `/docs` quick start for installation reminders.
