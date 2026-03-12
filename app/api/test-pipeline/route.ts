/**
 * Test Pipeline Route — DEV ONLY
 *
 * Runs the exact same pipeline as the chat UI but without auth.
 * Use this for A/B testing LLM providers (Gemini vs Claude).
 *
 * Usage:
 *   curl "http://localhost:8081/api/test-pipeline?prompt=Create+a+low-poly+chair"
 *   curl -X POST http://localhost:8081/api/test-pipeline \
 *     -H "Content-Type: application/json" \
 *     -d '{"prompt":"Create a low-poly medieval sword"}'
 *
 * Returns JSON with plan, code, and timing info.
 */

import { NextRequest, NextResponse } from "next/server"
import { generatePlan, generateCode } from "@/lib/ai/chains"
import { similaritySearch } from "@/lib/ai/vectorstore"
import { formatContextFromSources } from "@/lib/ai/rag"

// Define the tools available (same as BlenderAgent)
const MCP_TOOLS = [
  "get_scene_info",
  "get_object_info",
  "get_all_object_info",
  "get_viewport_screenshot",
  "execute_code",
  "get_polyhaven_status",
  "get_polyhaven_categories",
  "search_polyhaven_assets",
  "download_polyhaven_asset",
  "set_texture",
  "get_hyper3d_status",
  "create_rodin_job",
  "poll_rodin_job_status",
  "import_generated_asset",
  "get_sketchfab_status",
  "search_sketchfab_models",
  "download_sketchfab_model",
]

export async function GET(req: NextRequest) {
  // Block in production
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Test endpoint disabled in production" }, { status: 403 })
  }

  const prompt = req.nextUrl.searchParams.get("prompt")
  if (!prompt) {
    return NextResponse.json({
      error: "Missing ?prompt= parameter",
      usage: "curl 'http://localhost:8081/api/test-pipeline?prompt=Create+a+low-poly+chair'",
    }, { status: 400 })
  }

  return runPipeline(prompt)
}

export async function POST(req: NextRequest) {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Test endpoint disabled in production" }, { status: 403 })
  }

  const body = await req.json().catch(() => ({})) as { prompt?: string }
  const prompt = body.prompt
  if (!prompt) {
    return NextResponse.json({ error: "Missing 'prompt' in body" }, { status: 400 })
  }

  return runPipeline(prompt)
}

async function runPipeline(prompt: string) {
  const provider = (process.env.AI_PROVIDER ?? "gemini").toLowerCase()
  const model = provider === "anthropic" || provider === "claude"
    ? (process.env.ANTHROPIC_MODEL ?? "claude-opus-4-6")
    : (process.env.GEMINI_MODEL ?? "gemini-2.5-pro")
  const timings: Record<string, number> = {}
  const results: Record<string, unknown> = {}

  console.log(`\n${"=".repeat(60)}`)
  console.log(`[TEST] Pipeline Test — Provider: ${provider}, Model: ${model}`)
  console.log(`[TEST] Prompt: "${prompt}"`)
  console.log(`${"=".repeat(60)}\n`)

  try {
    // ── Step 1: RAG Retrieval ──────────────────────────────
    let ragContext = ""
    const ragStart = Date.now()
    try {
      const sources = await similaritySearch(prompt, {
        limit: 5,
        source: "blender-scripts",
        minSimilarity: 0.4,
      })
      ragContext = formatContextFromSources(sources)
      timings.rag_ms = Date.now() - ragStart
      results.rag = {
        documentsFound: sources.length,
        contextLength: ragContext.length,
        sources: sources.map(s => ({
          title: s.metadata?.title ?? s.metadata?.source ?? "unknown",
          similarity: s.similarity?.toFixed(3),
        })),
      }
      console.log(`[TEST] RAG: ${sources.length} documents, ${ragContext.length} chars (${timings.rag_ms}ms)`)
    } catch (ragErr) {
      timings.rag_ms = Date.now() - ragStart
      results.rag = { error: String(ragErr) }
      console.log(`[TEST] RAG failed: ${ragErr}`)
    }

    // ── Step 2: Plan Generation ──────────────────────────────
    const planStart = Date.now()
    const planResult = await generatePlan({
      request: prompt,
      tools: MCP_TOOLS,
      context: ragContext,
      sceneState: JSON.stringify({
        scene: "Scene",
        objects: [
          { name: "Camera", type: "CAMERA" },
          { name: "Light", type: "LIGHT" },
        ],
      }),
    })
    timings.plan_ms = Date.now() - planStart
    results.plan = {
      steps: planResult.plan.steps.map((s, i) => ({
        step: i + 1,
        action: s.action,
        rationale: s.rationale,
        expected_outcome: s.expected_outcome,
        hasCode: !!s.parameters?.code,
        hasDescription: !!s.parameters?.description,
      })),
      dependencies: planResult.plan.dependencies,
      warnings: planResult.plan.warnings,
      reasoning: planResult.reasoning?.slice(0, 500),
    }
    console.log(`[TEST] Plan: ${planResult.plan.steps.length} steps (${timings.plan_ms}ms)`)
    for (const [i, step] of planResult.plan.steps.entries()) {
      console.log(`  ${i + 1}. ${step.action}: ${step.rationale.slice(0, 80)}`)
    }

    // ── Step 3: Code Generation ──────────────────────────────
    // Find the first execute_code step description
    const codeStep = planResult.plan.steps.find(s => s.action === "execute_code")
    if (codeStep) {
      const codeDescription = typeof codeStep.parameters?.description === "string"
        ? codeStep.parameters.description
        : codeStep.rationale ?? codeStep.expected_outcome ?? prompt

      const codeStart = Date.now()
      const code = await generateCode({
        request: codeDescription,
        context: ragContext,
        applyMaterials: true,
        namingPrefix: "ModelForge_",
      })
      timings.codegen_ms = Date.now() - codeStart
      results.code = {
        length: code.length,
        lines: code.split("\n").length,
        snippet: code.slice(0, 2000),
        full: code,
      }
      console.log(`[TEST] Code: ${code.split("\n").length} lines, ${code.length} chars (${timings.codegen_ms}ms)`)
      console.log(`\n--- Generated Code (first 80 lines) ---`)
      code.split("\n").slice(0, 80).forEach((line, i) => console.log(`  ${String(i + 1).padStart(3)}: ${line}`))
      if (code.split("\n").length > 80) console.log(`  ... (${code.split("\n").length - 80} more lines)`)
      console.log(`--- End Code ---\n`)
    } else {
      results.code = { skipped: "No execute_code step in plan" }
      console.log(`[TEST] Code: skipped (no execute_code step)`)
    }

    // ── Summary ──────────────────────────────────────────
    timings.total_ms = Object.values(timings).reduce((a, b) => a + b, 0)
    console.log(`\n[TEST] Total: ${timings.total_ms}ms`)
    console.log(`[TEST] Provider: ${provider} | Model: ${model}`)
    console.log(`${"=".repeat(60)}\n`)

    return NextResponse.json({
      success: true,
      provider,
      model,
      prompt,
      timings,
      ...results,
    }, { status: 200 })

  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err)
    console.error(`[TEST] Pipeline error: ${errorMsg}`)
    return NextResponse.json({
      success: false,
      provider,
      model,
      prompt,
      error: errorMsg,
      timings,
      ...results,
    }, { status: 500 })
  }
}
