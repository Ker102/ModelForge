# gemini.md — ModelForge Dev Tracker

## Current Task
Filesystem reorganization (complete)

## What Changed (Latest)
- **Filesystem Reorganization**:
  - Root decluttered: 5 docs moved to `docs/`, 3 stale files deleted
  - `batch_scrape_markdown(8)/(9)` → `data/blender-api-docs/`
  - `scripts/` organized into `db/`, `ingestion/`, `test/`, `maintenance/`
  - `logs/` old sessions archived to `logs/archive/`
  - `tmp/` added to `.gitignore`
- **Studio Chat Persistence**:
  - `studio-layout.tsx` — localStorage save/load for workflow steps
  - `workflow-timeline.tsx` — 'Clear' button + `onClearTimeline` prop
- **Auth Pages Teal Redesign** + **BETA Badge on Blender Agent**

## Previous Changes
- CodeRabbit Fixes (PR #21): DEFAULT_MODEL, status validation, error scrolling
- Phase 5: Material/Lighting/Camera/Render tools (8 new tools)
- Phase 1-4: Transform, Modifier, Hierarchy/Export, Addon Detection tools

## Next Steps
- Debug agent tool execution failure (all steps show red X)
- Push + PR for CodeRabbit review
- DB-backed Studio session persistence (P1)
