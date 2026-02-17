# GEMINI.md - ModelForge Project Rules & Progress Tracker

> **Last Updated:** 2026-02-17
> **Status:** Active Development — 127 RAG scripts, fine-tuning pipeline ready

---

## 📋 Project Overview

**ModelForge** is an AI-powered Blender assistant that enables users to create, modify, and enhance Blender projects through natural conversation.

### Tech Stack
| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 16, React 19, TypeScript 5.6, Tailwind CSS 3.4 |
| **Backend** | Node.js 24+, PostgreSQL 14+ with pgvector (Neon serverless) |
| **ORM** | Prisma 5.20 |
| **Auth** | Supabase Auth (NextAuth fully removed) |
| **UI** | shadcn/ui, Radix UI, Lucide Icons |
| **Desktop** | Electron |
| **AI** | Google Gemini 2.5 Pro via @langchain/google-genai |
| **RAG** | Neon pgvector + Together.ai gte-modernbert-base (768d) |
| **Payments** | Stripe (Free/$12 Starter/$29 Pro) |

### Core Features
- 🤖 **AI Orchestration**: ReAct-style planner with per-step validation
- 🔌 **Blender MCP Integration**: Socket bridge for executing Python in Blender
- 📚 **Hybrid RAG Pipeline**: Context-aware generation using 127 professional Blender scripts
- 🌐 **Web Dashboard**: Project management, auth, conversation history
- 🖥️ **Desktop App**: Electron wrapper with native MCP connectivity

---

## 📁 Project Structure

```
ModelForge/
├── app/                    # Next.js app directory
├── components/            # React components
├── data/
│   └── blender-scripts/   # Library of 124 Python scripts
│       ├── tasks/        # Task-specific generators
│       └── *.py          # Utility modules
├── lib/                   # Utility libraries
│   ├── ai/               # RAG, Embeddings, VectorStore
│   ├── orchestration/    # Planner, Executor
│   └── mcp/              # Blender MCP Client
├── prisma/               # Database schema
├── desktop/              # Electron application
└── scripts/              # Ingestion and utility scripts
```

---

## 🔧 Development Commands

```bash
# Development
npm run dev              # Start Next.js dev server (port 3000)
npm run ingest:blender   # Ingest Blender scripts into RAG pipeline

# Database
npm run db:push          # Push schema to database
npm run db:studio        # Open Prisma Studio

# Testing
npm run test:user        # Create test user
```

---

## 📜 Agent Rules

### ⚡ Before EVERY Commit
1. **Update this file** (`GEMINI.md`) with:
   - Any new features or changes made
   - Updated progress tracking
2. **Run linting**: `npm run lint`
3. **Stage and commit** with descriptive messages:
   - `feat:` new features
   - `fix:` bug fixes
   - `docs:` documentation changes

### 🎯 Coding Standards
- **TypeScript**: Strict typing, avoid `any`
- **RAG First**: Always check existing scripts before generating new code
- **Components**: Functional components with Hooks
- **Styling**: Tailwind CSS utility classes

---

## 📊 Progress Tracking

### Current Sprint
| Task | Status | Notes |
|------|-----------|-------|
| Initial project setup | ✅ Complete | Next.js 16 + all integrations |
| Authentication system | ✅ Complete | Supabase Auth (NextAuth removed) |
| AI Orchestration layer | ✅ Complete | Planner, Executor, Prompts |
| **Serverless DB Migration** | ✅ Complete | Neon pgvector compatibility |
| **AI Engineering Upgrade** | ✅ Complete | LangChain, Agents, RAG implemented |
| **Script Library Expansion** | ✅ Complete | **127 scripts** (56 utility + 67 tasks + 4 NotebookLM) |
| **RAG Pipeline Ingestion** | ✅ Complete | Recursive ingestion of all scripts |
| **Viewport Screenshot Analysis** | ✅ Complete | Gemini Vision feedback loop |
| **Conversation Memory** | ✅ Complete | Vector embeddings for context-aware responses |
| **RAG in Code Generation** | ✅ Complete | Reference scripts injected before each code gen step |
| **LLM Scene Completeness Check** | ✅ Complete | Gemini verifies final scene matches user request |
| **Validation Hardening** | ✅ Complete | Auto-validate read-only commands, robust content parsing |
| **End-to-End Testing** | ✅ Complete | 3/3 stress tests passed (castle, solar system, edit) |
| **Orchestration Hardening** | ✅ Complete | Boolean solver, viewport shading, null safety fixes |
| **NotebookLM Knowledge Enhancement** | ✅ Complete | 4 new scripts, 18 API compat categories, 6 prompt sections |

### Roadmap
- [x] Gemini-backed conversational planning
- [x] Detailed plan auditing (components, materials, lighting)
- [x] Electron desktop shell
- [x] RAG Pipeline (100+ scripts)
- [x] **Viewport screenshot analysis**
- [x] **Conversation memory with vector embeddings**
- [x] **RAG integrated into code generation phase**
- [x] **LLM scene completeness validation**
- [x] **Stress testing with complex prompts (3/3 passed)**
- [x] **NotebookLM knowledge extraction + RAG enhancement**
- [x] **Fine-tuning pipeline (269 training pairs, QLoRA, eval framework)**
- [ ] Material/color quality enhancement
- [ ] Production desktop app packaging

---

## 📝 Session Log

### 2026-02-17 (Fine-Tuning Pipeline + Displacement Textures)
- **Training Data Pipeline**:
  - Created `scripts/generate-training-data.ts` — parses 125 RAG scripts into instruction→output pairs
  - Generated 269 training pairs (125 full-script + 144 function-level) in `training/training_data.jsonl`
  - Created `training/eval_prompts.json` — 50 held-out test prompts across all categories
  - Created `training/train_blender_codegen.py` — QLoRA (4-bit NF4) training script for Azure A100
  - Target model: Qwen3-8B, method: QLoRA, focus: Blender code generation only
- **New RAG Script**: `displacement_textures.py` (raked sand, water ripples, rocky terrain, modifier-based displacement)
- **Zen Garden Stress Test**: 7/7 steps, 0 failures, LLM completeness check passed
  - Scene: raked sand floor, 3 asymmetric stones, red torii gate, warm area lighting
  - Gap found: sand lacked wave/raked texture → fixed with new displacement script
- **Re-ingested**: 125 scripts into pgvector

### 2026-02-17 (NotebookLM Knowledge Enhancement)
- **NotebookLM MCP Integration**:
  - Installed `notebooklm-mcp-cli` v0.3.2, authenticated with Google
  - Queried "Mastering Blender Automation" notebook (89 sources)
  - Extracted ~36KB of expert knowledge across 5 deep queries
- **Scraped 15 Blender Docs** (via Firecrawl → `data/notebooklm-sources/`, ~268KB)
- **New RAG Scripts** (4 new, total 124):
  - `blender_api_pitfalls.py` — 15 common API pitfalls with solutions
  - `professional_materials.py` — PBR metals, glass, SSS, thin film recipes
  - `render_settings.py` — Cycles/EEVEE config, AgX color management
  - `volumetric_effects.py` — Atmosphere, fog, god rays, HDRI setup
- **Updated `api_version_compatibility.py`**: 8 → 18 Blender 5.0 breaking change categories
- **Enhanced `CODE_GENERATION_PROMPT`**: 6 new sections (factory pattern, mesh validation, light units, PBR materials, render/color management, volumetrics)
- **Re-ingested**: 124 scripts into pgvector (37 categories)

### 2026-02-16 (Firecrawl Scraping + API Compatibility)
- **Scraped Sources** (via Firecrawl):
  - Blender official best practices docs
  - Blender tips & tricks docs
  - CGWire shader guide (procedural materials via Python)
  - Blender 5.0 Python API release notes (all breaking changes)
  - Blender 4.0 Python API release notes
  - Stack Exchange shader node examples
- **New RAG Scripts** (2 new, total 120):
  - `api_version_compatibility.py` — Blender 5.0/4.0 breaking changes reference
  - `procedural_shader_recipes.py` — Noise, voronoi, gradient, worn-metal materials
- **Prompt Updates**: Added procedural shader and scene grounding guidance to `CODE_GENERATION_PROMPT`
- **Re-ingested**: 120 scripts into pgvector (materials:6, lighting:5, camera:2, scene:3, utility:1)

### 2026-02-16 (Professional Knowledge Enhancement)
- **New RAG Scripts** (5 new, total 118):
  - `vibrant_color_palettes.py` — 60+ saturated RGB constants for nature/space/metals/neon
  - `emission_materials.py` — Best practices for emissive materials (sun/neon/fire/screen)
  - `lighting_recipes.py` — Professional lighting: 3-point, studio, outdoor, sunset, dramatic, HDRI
  - `camera_composition.py` — Focal lengths, DOF, Track To, turntable, render settings
  - `scene_composition.py` — Real-world scale refs, floor planes, backdrops, pedestals, layouts
- **Prompt Update**: Added `MATERIAL COLORS — CRITICAL` to `CODE_GENERATION_PROMPT`
- **Re-ingested**: 118 scripts into pgvector (materials:5, lighting:5, camera:2, scene:3)

### 2026-02-16 (Orchestration Debugging + Stress Testing)
- **Viewport Material Preview**: Added automatic viewport switch to Material Preview after execution so materials are visible
- **Boolean Solver Fix**: Added Blender 5.x boolean guidance to `CODE_GENERATION_PROMPT` — `FAST` solver doesn't exist, only `EXACT`/`FLOAT`/`MANIFOLD`
- **Planning Rule #9**: "NEVER plan boolean operations for simple architectural details" — use separate geometry instead
- **LLM Completeness Check**: Made lenient for merged/joined objects; wrapped in try-catch for null safety
- **Gemini Model Alignment**: Updated all model references to `gemini-2.5-pro`, added `GEMINI_MODEL` env var
- **Removed Outdated Files**: Deleted `Orchesrecommendations.md`, `orchesproblems.md`, removed `auditCarScene` heuristic
- **Files Modified**: `lib/orchestration/executor.ts`, `lib/ai/prompts.ts`, `lib/gemini.ts`, `lib/stripe.ts`, `.env`
- **Stress Test Results**:
  - ✅ Castle (creation): 5 steps, 0 retries, 7 objects, 5 materials
  - ✅ Solar System (creation): 5 steps, 0 retries, 6 objects, 7 materials
  - ✅ Solar System Edit (scene editing): 4 steps, 0 retries, 18 objects, 9 materials
- **Remaining**: Material color quality is too muted — needs enhanced RAG scripts for vibrant colors

### 2026-02-16 (RAG Fix + Validation Hardening + End-to-End Testing)
- **Critical RAG Bug Fixed**: Vector store data ingested under source label `"blender-scripts"` but ALL queries used `"blender-docs"` → RAG always returned 0 results. Fixed in 4 files:
  - `lib/ai/agents.ts` — default `ragSource` → `"blender-scripts"`
  - `lib/ai/rag.ts` — default `source` → `"blender-scripts"`
  - `lib/orchestration/planner.ts` — explicit `ragSource` → `"blender-scripts"`
  - `lib/orchestration/executor.ts` — `source` → `"blender-scripts"`
- **RAG Added to Code Generation Phase**:
  - `executor.ts` now calls `similaritySearch()` before each `generateCode()` call
  - Retrieved scripts injected as `## Reference Blender Python Scripts` in context
  - Logged as `rag_retrieval` entries in execution log
- **LLM Scene Completeness Check Added**:
  - New `llmSceneCompletenessCheck()` method in `executor.ts`
  - Uses Gemini (temp 0.1) to verify final scene objects/materials/positions match user request
  - Returns `{ complete: boolean, issues: string[] }` — non-fatal on error
  - Integrated into `auditScene()` after structural checks
  - Now logs results as `llm_completeness_check` entries
- **Gemini Response Content Parsing Hardened**:
  - `response.content` from Gemini can be string OR array of content parts
  - Added `extractContent()` helper in `lib/ai/chains.ts`
  - Fixed ALL 5 call sites that used unsafe `response.content as string` cast
  - Also fixed in `executor.ts` `llmSceneCompletenessCheck()`
- **Validation Cascade Failure Fixed**:
  - `get_scene_info` was sent to LLM validation → Gemini returned unparseable response → all steps skipped
  - Expanded auto-validation to all read-only MCP commands: `get_scene_info`, `get_object_info`, `get_all_object_info`, `get_viewport_screenshot`, `get_polyhaven_status`, `get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset`, `set_texture`
  - These now auto-validate on `isMcpSuccess()` like `execute_code` does
- **Files Modified**:
  - `lib/ai/chains.ts` — Added `extractContent()`, fixed all `response.content` casts
  - `lib/ai/agents.ts` — Expanded auto-validation set, fixed RAG source default
  - `lib/ai/rag.ts` — Fixed default source filter
  - `lib/orchestration/executor.ts` — RAG retrieval, LLM completeness check, logging, source filter fix
  - `lib/orchestration/planner.ts` — Fixed ragSource
- **Test Results**:
  - ✅ Red metallic sphere + green pedestal — 4 steps, 0 retries, correct
  - ✅ Edit scene: add floor + orbiting spheres — preserved existing objects, RAG returned 5 sources/step
  - ❌ Medieval castle — failed due to validation cascade (now fixed, needs re-test)
- **Immediate Next Steps**:
  1. Re-test castle prompt (fix is hot-reloaded)
  2. Try spiral staircase (procedural), three-point lighting (edit), car scene (car audit)
  3. Continue iterating on code gen quality

### 2026-02-05 (WIP - Electron OAuth Session Persistence)
- **Electron OAuth Flow Debugging** (IN PROGRESS):
  - Investigating redirect loop after Google OAuth authentication
  - Issue: Cookies set via API routes not persisting to subsequent requests
  - **Files Modified**:
    - `app/api/auth/set-session/route.ts` - Server-side session setting API
    - `app/api/auth/set-session-redirect/route.ts` - Combined session set + redirect API
    - `components/auth/electron-auth-listener.tsx` - Listens for tokens from Electron
    - `middleware.ts` - Added debug logging for cookie inspection
  - **Root Cause Analysis**:
    - Cookies are being set correctly on API response (confirmed in logs)
    - Origin mismatch fixed (127.0.0.1 vs localhost)
    - Cookies not being sent with subsequent `/dashboard` requests
    - Redirect loop: `/dashboard` → `/login` → `/dashboard`
  - **Files Created**:
    - `app/api/auth/set-session-redirect/route.ts` - Sets cookies AND redirects in one response
  - **Debug Logging Added**:
    - Middleware now logs cookie presence and user auth status
    - Run `npm run dev` and check console for `[Middleware]` logs
  - **Next Steps for Continuation**:
    1. Check middleware logs to see if auth cookies are present on `/dashboard` requests
    2. If cookies missing: Investigate Electron session/cookie storage
    3. If cookies present but user null: Debug Supabase `getUser()` call
    4. Consider alternative: Store session token in Electron and pass via header

### 2026-01-21
- **Custom ModelForge Blender Addon**:
  - Created `desktop/assets/modelforge-addon.py` with branded UI
  - Panel under "ModelForge" tab with status indicator (●/○)
  - Organized UI with Settings and Asset Sources sections
  - Added IPC handlers: `addon:get-path`, `addon:open-folder`
- **Addon Setup Page**:
  - Created `app/setup/page.tsx` with step-by-step installation guide
  - Cross-platform path detection (Windows/macOS/Linux)
  - "Open Addon Folder" button for easy access
- **Supabase Auth Migration**:
  - Created `lib/supabase/` with client, server, and middleware utilities
  - Replaced NextAuth with Supabase auth in middleware
  - Updated login/signup forms and pages to use Supabase
  - Created OAuth callback route at `app/auth/callback/`
  - Added Supabase environment variables

### 2026-01-18
- **Test Scripts**:
  - Created `scripts/test-vision.ts` for vision module testing
  - Created `scripts/test-memory.ts` for memory service testing
  - Added npm test commands: `test:vision`, `test:memory`, `test:rag`
- **Desktop Production Build**:
  - Configured `electron-builder` for Windows/Mac/Linux distribution
  - Enhanced `main.js` with bundled server support
  - Users download installer → runs standalone (no setup required)
  - Updated `desktop/README.md` with build instructions

### 2026-01-16
- **Agent Rules File**:
  - Created `.cursor/rules.md` for coding agent instructions
  - Added to `.gitignore` to keep local
- **Conversation Memory Implementation**:
  - Added `embedding` field to Message model (768-dim pgvector)
  - Created `lib/memory/service.ts` with ConversationMemory class
  - Implemented: `storeMessage()`, `retrieveContext()`, `clearMemory()`
  - Integrated into BlenderPlanner with `useMemory` option
  - Enables context-aware planning from past conversations

### 2026-01-14
- **Viewport Screenshot Analysis Implementation**:
  - Created `lib/mcp/screenshot.ts` for viewport capture via MCP
  - Created `lib/ai/vision.ts` with LangChain Gemini multimodal integration
  - Added vision methods to `BlenderAgent`: `captureAndAnalyzeViewport()`, `validateStepVisually()`
  - Updated `ExecutionOptions` with `enableVisualFeedback` and `maxVisualIterations`
  - Added `visualValidation` field to `ExecutionLogEntry`
  - Enables dynamic feedback loop: model sees viewport → analyzes with Gemini → adjusts

### 2026-01-13
- Renamed project tracker to `GEMINI.md`
- **Script Library Expansion**:
  - Expanded library to **113 scripts** (exceeded 100 target)
  - Added comprehensive utility modules: `sculpt_utils`, `weight_paint`, `geonodes`, `texture_paint`
  - Added 60+ task-based generators in `tasks/` subdirectory
- **RAG Pipeline Completion**:
  - Updated `scripts/ingest-blender-docs.ts` to support recursive directory scanning
  - Successfully ingested all 113 scripts into Neon pgvector database
  - Verified embedding generation with Together.ai M2-BERT model
- **Documentation**:
  - Updated README.md and GEMINI.md to reflect new capabilities
---

## 📜 Agent Rules

### ⚡ Before EVERY Commit
1. **Update this file** (`Claude.md`) with:
   - Any new features or changes made
   - Updated progress tracking
   - New issues discovered
2. **Run linting**: `npm run lint`
3. **Stage and commit** with descriptive messages following conventional commits:
   - `feat:` new features
   - `fix:` bug fixes
   - `docs:` documentation changes
   - `refactor:` code refactoring
   - `style:` formatting changes

### 🎯 Coding Standards
- **TypeScript**: Use strict typing, avoid `any`
- **Components**: Functional components with React hooks
- **Styling**: Tailwind CSS utility classes
- **State**: Server components by default, client components when needed
- **API Routes**: Use Next.js App Router conventions
- **Database**: Always use Prisma for database operations

### 🔐 Security
- Never commit secrets or API keys
- Use environment variables for all sensitive data
- Validate all user inputs with Zod schemas

---

## 📊 Progress Tracking

### Current Sprint
| Task | Status | Notes |
|------|--------|-------|
| Initial project setup | ✅ Complete | Next.js 15 + all integrations |
| Authentication system | ✅ Complete | NextAuth v5 with Google OAuth |
| Prisma schema | ✅ Complete | Users, Projects, Conversations, Messages |
| AI Orchestration layer | ✅ Complete | Planner, Executor, Prompts |
| Desktop Electron shell | ✅ Complete | Basic wrapper working |
| **Serverless DB Migration** | ✅ Complete | Neon config compatible |
| **AI Engineering Upgrade** | ✅ Complete | LangChain, Agents, RAG implemented |

### Roadmap (from README)
- [x] Gemini-backed conversational planning
- [x] Detailed plan auditing (components, materials, lighting)
- [x] Electron desktop shell
- [x] MCP orchestration logging
- [ ] Conversation memory with vector embeddings
- [ ] Viewport screenshot analysis
- [ ] Production desktop app packaging
- [ ] Team collaboration features

---

## 🐛 Known Issues

### 🔴 Electron OAuth Redirect Loop (Active Blocker)
- **Symptom**: After successful Google OAuth authentication, Electron shows blue screen due to redirect loop
- **Cause**: Cookies set in API response are not being sent with subsequent requests to `/dashboard`
- **Status**: Under investigation - debug logging added to middleware
- **Workaround**: None currently - OAuth in browser works fine, only Electron affected

## 📝 Session Log

### 2026-01-01
- Created `Claude.md` for project tracking and agent rules
- Created `Claude.md` for project tracking and agent rules
- Analyzed full project structure and documented tech stack
- **Architecture Upgrade Phase 1 (Database)**:
  - Selected Neon (serverless PostgreSQL) with pgvector
  - Updated `prisma/schema.prisma` with `directUrl` and `DocumentEmbedding` model
  - Configured `lib/db.ts` for serverless connection pooling
  - Updated `.env.example` with Neon and Together.ai keys
- **Architecture Upgrade Phase 2 (AI Engineering)**:
  - Integrated **LangChain.js** framework
  - Configured **Gemini 3 Pro Preview** as primary LLM
  - Configured **Together.ai M2-BERT** (768-dim) for embeddings
  - Created `lib/ai/` module:
    - `index.ts`: Core client initialization
    - `embeddings.ts`: M2-BERT integration
    - `vectorstore.ts`: Neon pgvector store
    - `rag.ts`: RAG pipeline with context-aware generation
    - `prompts.ts`: LangChain `PromptTemplate` system
    - `chains.ts`: Zod-validated planning/validation chains
    - `agents.ts`: ReAct-style Blender agent implementation

### Pending
- Refactored `lib/orchestration/planner.ts` to use new AI module (BlenderAgent)
- Refactored `lib/orchestration/executor.ts` to use new AI module (BlenderAgent)
- Updated `SETUP.md` with Neon instructions
- **Architecture Upgrade Phase 4 (RAG Population)**:
  - Created library of Blender Python scripts in `data/blender-scripts/`
  - Implemented `scripts/ingest-blender-docs.ts` for automated ingestion
  - Successfully populated Neon pgvector with initial documentation
  - Verified semantic retrieval with `scripts/test-rag.ts`
- **Script Library Enhancement (Phase 5)**:
  - Enhanced existing scripts: `mesh`, `material`, `scene`, `transform`
  - Created new scripts: `selection`, `clean`, `modifier`, `curve`, `text`
  - Re-ingested all scripts and verified with expanded queries
- Run migration and verification tests (Complete)

---

## 🔗 Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Auth Config | `lib/auth.ts` |
| Database Schema | `prisma/schema.prisma` |
| AI Planner | `lib/orchestration/planner.ts` |
| AI Executor | `lib/orchestration/executor.ts` |
| Gemini Integration | `lib/gemini.ts` |
| MCP Client | `lib/mcp/` |
| Main Layout | `app/layout.tsx` |
| API Routes | `app/api/` |
