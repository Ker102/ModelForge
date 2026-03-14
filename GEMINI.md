# gemini.md — ModelForge Dev Tracker

## Current Task
Phase 5 complete — Material/Lighting/Camera/Render tools

## What Changed (Latest)
- **CodeRabbit Fixes (PR #21)**:
  - DEFAULT_MODEL → `gemini-2.5-pro` in `lib/ai/index.ts` and `lib/gemini.ts`
  - Failed autopilot steps now correctly marked `"failed"` in `studio-layout.tsx`
  - Command status validated against union type in `studio-layout.tsx`
  - Error text scrollable (not truncated) in `step-session-drawer.tsx`
  - vectorLiteral() dimension validation in `vectorstore.ts`
- **Phase 5 — Material/Lighting/Camera/Render Tools** (8 new tools):
  - `create_material` — Principled BSDF with color/metallic/roughness
  - `assign_material` — assign material to object by slot
  - `add_light` — POINT/SUN/SPOT/AREA with energy/color/location
  - `set_light_properties` — modify existing light properties
  - `add_camera` — create camera with lens/position/rotation
  - `set_camera_properties` — lens/DoF/clip/set active
  - `set_render_settings` — engine/resolution/samples/denoising
  - `render_image` — render scene to file

## Previous Changes
- Phase 1-4: Transform, Modifier, Hierarchy/Export, Addon Detection tools
- LangChain v1 migration, agent refactoring, viewport screenshot middleware
- Curated addons page, README update

## Next Steps
- Push + PR for CodeRabbit review
- Feature brainstorm P2/P3 implementation
