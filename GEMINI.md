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

## Architecture Notes
- **Monitoring**: Unified pipeline monitoring in `lib/orchestration/monitor.ts`
  - Session logs: `logs/session-{id}.json`
  - Pipeline log: `logs/pipeline.log`
  - Orchestration: `logs/orchestration.ndjson`
  - Latest run: `logs/latest-run.json`

## Next Steps
- End-to-end test: verify follow-up text appears in UI after Blender agent execution
- Review CodeRabbit feedback on PR
