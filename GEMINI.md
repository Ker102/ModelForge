# gemini.md — ModelForge Dev Tracker

## Current Task
Blender 5.0+ Animation Script Migration — Slotted Actions API Update

## What Changed
- **Animation Scripts**: Migrated 3 scripts to Blender 5.0+ Slotted Actions API
  - `animation_utils.py` → `animation_utils_legacy.py` + new 5.0+ version
  - `procedural_animation.py` → `procedural_animation_legacy.py` + new 5.0+ version
  - `action_utils.py` → `action_utils_legacy.py` + new 5.0+ version
- **Root Cause**: `action.fcurves`, `action.groups`, `action.id_root` removed in Blender 5.0
- **Fix**: All fcurve access now uses `channelbag.fcurves` via `bpy_extras.anim_utils`
- **New Functions Added**:
  - `get_fcurves()` — channelbag-based fcurve retrieval
  - `ensure_fcurve()` — create fcurve in channelbag
  - `set_handle_type()` — keyframe handle control
  - `scale_pulse_animation()` — heartbeat/breathing effect
  - `shake_animation()` — camera shake/impact
  - `create_action_with_slot()` — slot-aware action creation
  - `list_action_slots()` — inspect action slots
  - `get_action_info()` — debug action hierarchy
- **api_version_compatibility.py**: Expanded section 11 with 70+ lines of Slotted Actions migration patterns
- **Deep Research**: 64 sources imported into NotebookLM on Blender 5.0 animation API

## Previous Changes
- **Prompt**: CODE_GENERATION_PROMPT 13K → 9.7K (removed RAG dupes)
- **RAG Scripts**: +10 new scripts (animation, physics, rendering, mesh factory)
- **Vectorstore**: 135 → 145 documents
- **LLM Provider**: Added Claude/Anthropic support via AI_PROVIDER env var

## Next Steps
- Re-embed ALL scripts into vector DB
- Re-test Motion category (test #6) — should pass without fcurves error
- Re-test Paint category (test #4) — verify material application
- Visual verification in Blender between each test
