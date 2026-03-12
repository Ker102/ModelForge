/**
 * Test Pipeline Route — DEV ONLY
 *
 * Runs the FULL pipeline (RAG → Plan → Code Gen → MCP Execute) without auth.
 * Use this for A/B testing LLM providers (Gemini vs Claude).
 *
 * Usage:
 *   # Plan + Generate + Execute in Blender
 *   curl -X POST http://localhost:8081/api/test-pipeline \
 *     -H "Content-Type: application/json" \
 *     -d '{"prompt":"Create a low-poly medieval sword"}'
 *
 *   # Plan + Generate only (skip Blender execution)
 *   curl -X POST http://localhost:8081/api/test-pipeline \
 *     -H "Content-Type: application/json" \
 *     -d '{"prompt":"Create a chair", "skipExecution": true}'
 *
 *   # Quick GET
 *   curl "http://localhost:8081/api/test-pipeline?prompt=Create+a+chair"
 *
 * Returns JSON with plan, code, execution results, and timing info.
 */

import { NextRequest, NextResponse } from "next/server"
import { generatePlan, generateCode } from "@/lib/ai/chains"
import { similaritySearch } from "@/lib/ai/vectorstore"
import { formatContextFromSources } from "@/lib/ai/rag"
import { createMcpClient, checkMcpConnection } from "@/lib/mcp"

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

  const skipExecution = req.nextUrl.searchParams.get("skipExecution") === "true"
  return runPipeline(prompt, skipExecution)
}

export async function POST(req: NextRequest) {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Test endpoint disabled in production" }, { status: 403 })
  }

  const body = await req.json().catch(() => ({})) as { prompt?: string; skipExecution?: boolean }
  const prompt = body.prompt
  if (!prompt) {
    return NextResponse.json({ error: "Missing 'prompt' in body" }, { status: 400 })
  }

  return runPipeline(prompt, body.skipExecution ?? false)
}

async function runPipeline(prompt: string, skipExecution = false) {
  const provider = (process.env.AI_PROVIDER ?? "gemini").toLowerCase()
  const model = provider === "anthropic" || provider === "claude"
    ? (process.env.ANTHROPIC_MODEL ?? "claude-opus-4-6")
    : (process.env.GEMINI_MODEL ?? "gemini-2.5-pro")
  const timings: Record<string, number> = {}
  const results: Record<string, unknown> = {}

  console.log(`\n${"=".repeat(60)}`)
  console.log(`[TEST] Pipeline Test — Provider: ${provider}, Model: ${model}`)
  console.log(`[TEST] Prompt: "${prompt}"`)
  console.log(`[TEST] Execute in Blender: ${!skipExecution}`)
  console.log(`${"=".repeat(60)}\n`)

  try {
    // ── Step 0: Check Blender MCP connection ──────────────────
    let mcpConnected = false
    let sceneState = JSON.stringify({
      scene: "Scene",
      objects: [
        { name: "Camera", type: "CAMERA" },
        { name: "Light", type: "LIGHT" },
      ],
    })

    if (!skipExecution) {
      console.log(`[TEST] Checking Blender MCP connection...`)
      const connCheck = await checkMcpConnection()
      mcpConnected = connCheck.connected
      results.mcpConnection = connCheck

      if (!mcpConnected) {
        console.log(`[TEST] ⚠ Blender not connected: ${connCheck.error}`)
        console.log(`[TEST] Continuing with plan+codegen only (no execution)`)
        results.mcpWarning = "Blender addon not connected — skipping execution"
      } else {
        console.log(`[TEST] ✓ Blender connected on port 9876`)
        // Get real scene info
        try {
          const client = createMcpClient()
          const sceneInfo = await client.execute({
            type: "get_scene_info",
            params: {},
          })
          sceneState = JSON.stringify(sceneInfo.result ?? sceneInfo)
          results.sceneStateBefore = sceneInfo.result ?? sceneInfo
          console.log(`[TEST] Scene state: ${sceneState.slice(0, 200)}`)
          await client.close()
        } catch (sceneErr) {
          console.log(`[TEST] Could not get scene info: ${sceneErr}`)
        }
      }
    }

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
      sceneState,
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
        parameters: s.parameters,
      })),
      dependencies: planResult.plan.dependencies,
      warnings: planResult.plan.warnings,
      reasoning: planResult.reasoning?.slice(0, 500),
    }
    console.log(`[TEST] Plan: ${planResult.plan.steps.length} steps (${timings.plan_ms}ms)`)
    for (const [i, step] of planResult.plan.steps.entries()) {
      console.log(`  ${i + 1}. ${step.action}: ${step.rationale.slice(0, 100)}`)
    }

    // ── Step 3: Code Generation for each execute_code step ──
    const codeSteps = planResult.plan.steps.filter(s => s.action === "execute_code")
    const generatedCodes: { description: string; code: string; lines: number }[] = []

    for (const [idx, codeStep] of codeSteps.entries()) {
      const codeDescription = typeof codeStep.parameters?.description === "string"
        ? codeStep.parameters.description
        : typeof codeStep.parameters?.code === "string"
          ? codeStep.parameters.code // already has inline code
          : codeStep.rationale ?? codeStep.expected_outcome ?? prompt

      // If the planner already provided code, use it directly
      if (typeof codeStep.parameters?.code === "string") {
        const code = codeStep.parameters.code as string
        generatedCodes.push({ description: codeDescription, code, lines: code.split("\n").length })
        console.log(`[TEST] Step ${idx + 1}/${codeSteps.length}: Using inline code (${code.split("\n").length} lines)`)
        continue
      }

      const codeStart = Date.now()
      const code = await generateCode({
        request: codeDescription,
        context: ragContext,
        applyMaterials: true,
        namingPrefix: "ModelForge_",
      })
      const codeMs = Date.now() - codeStart
      timings[`codegen_step${idx + 1}_ms`] = codeMs
      generatedCodes.push({ description: codeDescription, code, lines: code.split("\n").length })
      console.log(`[TEST] CodeGen step ${idx + 1}/${codeSteps.length}: ${code.split("\n").length} lines, ${code.length} chars (${codeMs}ms)`)
    }

    results.code = generatedCodes.map((gc, i) => ({
      step: i + 1,
      description: gc.description.slice(0, 200),
      lines: gc.lines,
      length: gc.code.length,
      snippet: gc.code.slice(0, 2000),
      full: gc.code,
    }))

    // Print the first code block to console
    if (generatedCodes.length > 0) {
      const mainCode = generatedCodes[0].code
      console.log(`\n--- Generated Code (first 80 lines) ---`)
      mainCode.split("\n").slice(0, 80).forEach((line, i) => console.log(`  ${String(i + 1).padStart(3)}: ${line}`))
      if (mainCode.split("\n").length > 80) console.log(`  ... (${mainCode.split("\n").length - 80} more lines)`)
      console.log(`--- End Code ---\n`)
    }

    // ── Step 4: Execute in Blender via MCP ──────────────────
    const executionResults: { step: number; status: string; output?: unknown; error?: string; time_ms: number }[] = []

    if (!skipExecution && mcpConnected && generatedCodes.length > 0) {
      console.log(`[TEST] 🚀 Executing ${generatedCodes.length} code block(s) in Blender...`)
      const client = createMcpClient()

      for (const [idx, gc] of generatedCodes.entries()) {
        const execStart = Date.now()
        try {
          console.log(`[TEST] Executing step ${idx + 1}/${generatedCodes.length}...`)
          const execResult = await client.execute({
            type: "execute_code",
            params: { code: gc.code },
          })
          const execMs = Date.now() - execStart
          timings[`exec_step${idx + 1}_ms`] = execMs

          const stepResult = {
            step: idx + 1,
            status: execResult.status ?? "unknown",
            output: execResult.result ?? execResult.message,
            time_ms: execMs,
          }
          executionResults.push(stepResult)
          console.log(`[TEST] ✓ Step ${idx + 1} executed (${execMs}ms): ${JSON.stringify(execResult.result ?? execResult.message).slice(0, 200)}`)
        } catch (execErr) {
          const execMs = Date.now() - execStart
          timings[`exec_step${idx + 1}_ms`] = execMs
          const errMsg = execErr instanceof Error ? execErr.message : String(execErr)
          executionResults.push({ step: idx + 1, status: "error", error: errMsg, time_ms: execMs })
          console.log(`[TEST] ✗ Step ${idx + 1} failed (${execMs}ms): ${errMsg}`)
        }
      }

      // Get final scene state
      try {
        const finalScene = await client.execute({
          type: "get_scene_info",
          params: {},
        })
        results.sceneStateAfter = finalScene.result ?? finalScene
        console.log(`[TEST] Final scene: ${JSON.stringify(results.sceneStateAfter).slice(0, 300)}`)
      } catch {
        console.log(`[TEST] Could not get final scene info`)
      }

      await client.close()
    } else if (!skipExecution && !mcpConnected) {
      console.log(`[TEST] ⏭ Skipped execution — Blender not connected`)
    } else {
      console.log(`[TEST] ⏭ Skipped execution (skipExecution=true)`)
    }

    results.execution = executionResults

    // ── Summary ──────────────────────────────────────────
    timings.total_ms = Object.values(timings).reduce((a, b) => a + b, 0)
    console.log(`\n[TEST] ${"─".repeat(40)}`)
    console.log(`[TEST] ✅ Pipeline complete`)
    console.log(`[TEST] Provider: ${provider} | Model: ${model}`)
    console.log(`[TEST] Total: ${timings.total_ms}ms`)
    console.log(`[TEST] Code steps: ${generatedCodes.length} | Executed: ${executionResults.length}`)
    if (executionResults.length > 0) {
      const successes = executionResults.filter(r => r.status !== "error").length
      console.log(`[TEST] Execution: ${successes}/${executionResults.length} succeeded`)
    }
    console.log(`${"=".repeat(60)}\n`)

    return NextResponse.json({
      success: true,
      provider,
      model,
      prompt,
      blenderConnected: mcpConnected,
      timings,
      ...results,
    }, { status: 200 })

  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err)
    const stack = err instanceof Error ? err.stack : undefined
    console.error(`[TEST] ❌ Pipeline error: ${errorMsg}`)
    if (stack) console.error(stack)
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
