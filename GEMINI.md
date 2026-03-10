# ModelForge – Active Development Notes

## Current Task
**Studio Pipeline Hardening** – Fixing Blender agent bugs and improving post-execution UX.

## Progress Summary
- Gemini API switched to `gemini-3.1-pro-preview` model with `v1beta` endpoint
- Studio `workflowMode` fixed: `autopilot` (not `studio`) for actual execution
- Monitoring system (MonitoringPanel, StepSessionDrawer) fully wired
- Session drawer now shows plan execution summary, command results, and pipeline monitor
- Added `StepPlanData` + `StepCommandResult` types for structured execution data
- Updated `complete` event handler to extract planning metadata and command suggestions
- **Fixed**: `get_viewport_screenshot` → `max_size` param instead of invalid `width`/`height`
- **Fixed**: Defensive param normalization in executor for LLM-hallucinated width/height
- **Fixed**: Gemini API `buildContents()` consecutive user messages bug (caused follow-up to silently fail)
- **Fixed**: Post-execution follow-up with visible error fallback in catch block
- **Fixed**: CRAG pipeline — `vectorstore.ts` used `::vector(768)` in Prisma tagged templates which PostgreSQL rejected. Switched to `Prisma.raw()` for type casts.
- **Fixed**: Embedding model — switched from Together.ai `GTE-ModernBERT-base` (deprecated) to Gemini `gemini-embedding-001` (768-dim, free). No DB migration needed.
- **Fixed**: Viewport screenshot — Blender MCP server requires `filepath` param. Added file-based fallback (read from disk if no inline base64).
- **Fixed**: `isMcpSuccess()` — now checks nested `result.error` BEFORE trusting top-level `status: "success"`.
- **Ingested**: 135 blender-scripts documents into pgvector vectorstore across 39 categories.

## Monitoring & Logging Reference
**IMPORTANT**: Always check these files when debugging the Blender agent pipeline.

### Unified Session Monitor (`lib/monitoring/logger.ts`)
- **Class**: `MonitoringSession` (created via `createMonitoringSession(sessionId)`)
- **Console output**: Colorized, structured logs in the Next.js dev server terminal
- **File output**: `logs/pipeline.log` — NDJSON, one JSON entry per log call
- **Session summary**: `logs/session-{first8chars-of-id}.json` — full session JSON (timers, counts, costs)
- **Namespaces**: planner, executor, crag, neural, vision, rag, strategy, mcp, workflow, system
- **Features**: Timers (`startTimer`/`endTimer`), neural cost tracking, RAG stats, log callbacks

### Execution Monitor (`lib/orchestration/monitor.ts`)
- **Function**: `recordExecutionLog(record)` — appends to `logs/orchestration.ndjson`
- **Content**: Full execution records with plan summary, command results, scene summary

### Log File Locations
| File | Content |
|------|---------|
| `logs/pipeline.log` | Per-entry NDJSON from MonitoringSession |
| `logs/session-{id}.json` | Full session summary (timers, costs, stats) |
| `logs/orchestration.ndjson` | Execution records (plan + command results) |
| `logs/latest-run.json` | Last execution record (legacy) |

### Visual Feedback Flow
1. `route.ts:626` sets `enableVisualFeedback: true`
2. `executor.ts:265-380` captures viewport screenshot via MCP (`get_viewport_screenshot`)
3. `executor.ts:315` calls `suggestImprovements(imageBase64, userRequest)` — Gemini Vision analysis
4. If high-priority issues found → generates correction code → executes fix → re-captures
5. Max 2 visual iterations by default (`maxVisualIterations ?? 2`)

## Next Steps
- End-to-end test: verify follow-up text appears in UI after Blender agent execution
- Review CodeRabbit feedback on PR
