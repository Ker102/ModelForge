# Claude.md - ModelForge Project Rules & Progress Tracker

> **Last Updated:** 2026-01-01  
> **Status:** Active Development

---

## 📋 Project Overview

**ModelForge** is an AI-powered Blender assistant that enables users to create, modify, and enhance Blender projects through natural conversation.

### Tech Stack
| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 15, React 19, TypeScript 5.6, Tailwind CSS 3.4 |
| **Backend** | Node.js 18+, PostgreSQL 14+ with pgvector |
| **ORM** | Prisma 5.20 |
| **Auth** | NextAuth.js v5 (Credentials + Google OAuth) |
| **UI** | shadcn/ui, Radix UI, Lucide Icons |
| **Desktop** | Electron |
| **AI** | Google Gemini 2.x API |
| **Payments** | Stripe |

### Core Features
- 🤖 **AI Orchestration**: ReAct-style planner with per-step validation
- 🔌 **Blender MCP Integration**: Socket bridge for executing Python in Blender
- 🌐 **Web Dashboard**: Project management, auth, conversation history
- 🖥️ **Desktop App**: Electron wrapper with native MCP connectivity
- 📊 **Subscription System**: Free, Starter ($12/mo), Pro ($29/mo) tiers

---

## 📁 Project Structure

```
ModelForge/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   ├── dashboard/         # Protected dashboard pages
│   ├── login/, signup/    # Auth pages
│   └── page.tsx           # Landing page
├── components/            # React components
│   ├── ui/               # shadcn/ui base components
│   ├── landing/          # Landing page sections
│   ├── dashboard/        # Dashboard components
│   └── auth/             # Auth forms
├── lib/                   # Utility libraries
│   ├── orchestration/    # AI orchestration (planner, executor, prompts)
│   ├── mcp/              # MCP client for Blender
│   ├── auth.ts           # NextAuth configuration
│   ├── db.ts             # Prisma client
│   └── gemini.ts         # Gemini API integration
├── prisma/               # Database schema
├── desktop/              # Electron application
└── scripts/              # Utility scripts
```

---

## 🔧 Development Commands

```bash
# Development
npm run dev              # Start Next.js dev server (port 3000)
npm run lint             # Run ESLint

# Database
npm run db:generate      # Generate Prisma client
npm run db:push          # Push schema to database
npm run db:migrate       # Run migrations
npm run db:studio        # Open Prisma Studio

# Testing
npm run test:user        # Create test user (test@modelforge.dev / TestPass123!)

# Desktop
cd desktop && npm run dev  # Start Electron app (requires web app running)
```

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
