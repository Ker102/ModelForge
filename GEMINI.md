# GEMINI.md - ModelForge Project Rules & Progress Tracker

> **Last Updated:** 2026-01-13
> **Status:** Active Development

---

## 📋 Project Overview

**ModelForge** is an AI-powered Blender assistant that enables users to create, modify, and enhance Blender projects through natural conversation.

### Tech Stack
| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 16, React 19, TypeScript 5.6, Tailwind CSS 3.4 |
| **Backend** | Node.js 24+, PostgreSQL 14+ with pgvector |
| **ORM** | Prisma 5.20 |
| **Auth** | NextAuth.js v5 (Credentials + Google OAuth) |
| **UI** | shadcn/ui, Radix UI, Lucide Icons |
| **Desktop** | Electron |
| **AI** | Google Gemini 3 Pro (Preview) |
| **RAG** | Neon pgvector + Together.ai M2-BERT (768d) |
| **Payments** | Stripe |

### Core Features
- 🤖 **AI Orchestration**: ReAct-style planner with per-step validation
- 🔌 **Blender MCP Integration**: Socket bridge for executing Python in Blender
- 📚 **Hybrid RAG Pipeline**: Context-aware generation using 113+ professional Blender scripts
- 🌐 **Web Dashboard**: Project management, auth, conversation history
- 🖥️ **Desktop App**: Electron wrapper with native MCP connectivity

---

## 📁 Project Structure

```
ModelForge/
├── app/                    # Next.js app directory
├── components/            # React components
├── data/
│   └── blender-scripts/   # Library of 113+ Python scripts
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
| Authentication system | ✅ Complete | NextAuth v5 with Google OAuth |
| AI Orchestration layer | ✅ Complete | Planner, Executor, Prompts |
| **Serverless DB Migration** | ✅ Complete | Neon pgvector compatibility |
| **AI Engineering Upgrade** | ✅ Complete | LangChain, Agents, RAG implemented |
| **Script Library Expansion** | ✅ Complete | **113 scripts** (46 utility + 67 tasks) |
| **RAG Pipeline Ingestion** | ✅ Complete | Recursive ingestion of all scripts |
| **Viewport Screenshot Analysis** | ✅ Complete | Gemini Vision feedback loop |
| **Conversation Memory** | ✅ Complete | Vector embeddings for context-aware responses |

### Roadmap
- [x] Gemini-backed conversational planning
- [x] Detailed plan auditing (components, materials, lighting)
- [x] Electron desktop shell
- [x] RAG Pipeline (100+ scripts)
- [x] **Viewport screenshot analysis**
- [x] **Conversation memory with vector embeddings**
- [ ] Production desktop app packaging

---

## 📝 Session Log

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

*No known issues at this time.*

---

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
