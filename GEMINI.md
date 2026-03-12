# gemini.md — ModelForge Dev Tracker

## Current Task
Multi-provider LLM abstraction + RAG enhancement for Blender agent

## What Changed
- **Prompt**: CODE_GENERATION_PROMPT 13K → 9.7K (removed RAG dupes)
- **RAG Scripts**: +10 new scripts (animation, physics, rendering, mesh factory)
- **Vectorstore**: 135 → 145 documents
- **LLM Provider**: Added Claude/Anthropic support via AI_PROVIDER env var
  - lib/anthropic.ts — zero-dep integration (direct API + Vertex AI)
  - lib/llm/index.ts — routed into provider union
  - pp/api/ai/chat/route.ts — reads AI_PROVIDER env var

## How to Switch Models
`ash
# .env
AI_PROVIDER=gemini          # default
AI_PROVIDER=anthropic       # switch to Claude
ANTHROPIC_API_KEY=sk-...    # for direct API
ANTHROPIC_MODEL=claude-opus-4-20250514  # default model

# OR for Vertex AI:
VERTEX_AI_PROJECT=my-project
VERTEX_AI_LOCATION=us-east5
VERTEX_AI_ACCESS_TOKEN=ya29...
`

## Pipeline Test (Sword)
- 4/4 steps passed, 0 failures, 0 retries
- Blade looks better but handle disconnected (code gen quality issue)

## Next Steps
- Test Claude Opus 4.6 via Vertex AI for code gen comparison
- Continue improving code gen quality
