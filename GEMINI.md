# gemini.md — ModelForge Dev Tracker

## Current Task
Agent Iteration Behavior & Viewport Screenshot Observability

## What Changed (Latest)
- **System Prompt Rewrite** (`blender-agent-system.md`):
  - Rewrote Example 1 from "one go" → iterative with viewport verification
  - Added Example 4: Complex forge scene built component-by-component with 3 screenshot checkpoints
  - Added "Iterative Refinement" rule: unlimited execute_code calls, quality over speed
  - Every example now includes `get_viewport_screenshot` verification
- **Planner Prompt Fixes** (`lib/ai/prompts.ts`):
  - Rule #8: Changed from "Prefer fewer steps" → "Break into SEPARATE execute_code steps"
  - Added Rule #13: Viewport verification after major geometry creation
- **Orchestration Prompts** (`lib/orchestration/prompts.ts`):
  - Rule #2: Changed from "tackle explicitly" → "tackle in SEPARATE execute_code call"
  - Rule #6: Changed from "confirm progress" → "use get_viewport_screenshot to verify"
  - Added viewport verification steps to Examples 1 and 3
- **Screenshot Observability** (`executor.ts`):
  - Added automatic viewport screenshot after every execute_code step
  - Screenshots logged as vision events and streamed to client
  - Failures logged as WARNING (visible) instead of silently swallowed

## Previous Changes
- Migrated 3 animation scripts to Blender 5.0+ Slotted Actions API
- Added new animation functions (scale_pulse, shake, ensure_fcurve, etc.)
- Deep research: 64 sources from NotebookLM on Blender 5.0 animation API

## Next Steps
- Re-embed ALL scripts into vector DB
- Re-test Motion category — verify no fcurves errors
- Visual verification in Blender with new iterative behavior
