# ModelForge Project Notes

## Current Status (2026-02-06)
- **Auth**: Fully migrated to Supabase Auth. NextAuth removed entirely. Login, signup, dashboard access, and sign-out all verified working in both browser and Electron.
- **Web app**: AI chat with Gemini streaming, MCP connection card, usage tracking, docs/quick start fully updated.
- **Desktop app**: Electron shell wraps web dashboard on port 3000; quick start/usage cards visible. OAuth via deep-link flow.
- **MCP**: Socket client + `/api/mcp/status` + `/api/mcp/execute`; addon available at `/downloads/modelforge-addon.py`.
- **RAG pipeline**: 113+ Blender scripts ingested into Neon pgvector for context-aware code generation.
- **Orchestration**: Two-phase planner/executor (Gemini generates JSON plan → step-by-step execution with validation/recovery).
- **Monetization**: Stripe integration with Free / Starter ($12/mo) / Pro ($29/mo) tiers.

## Completed Milestones
- [x] Supabase Auth migration (removed NextAuth, @auth/prisma-adapter, bcryptjs)
- [x] Auto-provisioning of Prisma user records on first Supabase login
- [x] Stripe customer sync on auth (idempotent background task)
- [x] Electron app loads correctly from Next.js dev server (port 3000)
- [x] Middleware cleaned up (no debug logging, protects /dashboard and /generate)

## Outstanding Work
1. Test and iterate on orchestration quality (Gemini plan generation, code execution in Blender via MCP).
2. Integrate viewport screenshots / MCP results into UI (web & desktop).
3. Package Electron app for distribution (auto-update, installers).
4. Deploy to production (DigitalOcean / Vercel) with production database.
5. Add tests/monitoring for MCP connection and error handling.

## Suggested Next Steps
1. Connect to Blender via MCP and test end-to-end scene generation.
2. Iterate on orchestration plan quality and code execution reliability.
3. Package & release desktop app (auto-update pipeline).

Refer to `blendermcpreadme.md` and `/docs` quick start for installation reminders.
