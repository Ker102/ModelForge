import { randomUUID } from "crypto"

import { generateGeminiResponse } from "@/lib/gemini"
import { createMcpClient } from "@/lib/mcp"
import type { McpCommand } from "@/lib/mcp"
import { ExecutionLogEntry, ExecutionPlan, PlanStep } from "./types"

export interface ExecutionResult {
  success: boolean
  completedSteps: Array<{ step: PlanStep; result: unknown }>
  failedSteps: Array<{ step: PlanStep; error: string }>
  finalSceneState?: unknown
  logs: ExecutionLogEntry[]
}

const VALIDATION_SYSTEM_PROMPT = `You are validating the outcome of a Blender MCP command. Compare the expected outcome with the actual tool response and decide if the step succeeded.`

const VALIDATION_OUTPUT_FORMAT = `Return strict JSON with:
{
  "success": true|false,
  "reason": "short explanation",
  "concerns": ["optional warnings"]
}`

const RECOVERY_SYSTEM_PROMPT = `You are assisting with recovery after a Blender MCP command failed. Suggest a single corrective action if possible.`

const RECOVERY_OUTPUT_FORMAT = `Return strict JSON with:
{
  "recovery_action": "tool_name or null",
  "recovery_params": { ... },
  "explanation": "why this helps"
}`

export class PlanExecutor {
  async executePlan(plan: ExecutionPlan, userRequest: string): Promise<ExecutionResult> {
    const client = createMcpClient()
    const logs: ExecutionLogEntry[] = []
    const completedSteps: Array<{ step: PlanStep; result: unknown }> = []
    const failedSteps: Array<{ step: PlanStep; error: string }> = []

    try {
      for (const step of plan.steps) {
        const command: McpCommand = {
          id: randomUUID(),
          type: step.action,
          params: step.parameters,
        }

        let result: unknown
        try {
          result = await client.execute(command)
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            result,
          })
        } catch (error) {
          const message = error instanceof Error ? error.message : "Command execution failed"
          logs.push({
            timestamp: new Date().toISOString(),
            tool: step.action,
            parameters: step.parameters,
            error: message,
          })
          failedSteps.push({ step, error: message })
          return { success: false, completedSteps, failedSteps, logs }
        }

        const validation = await this.validateStep(step, result, userRequest)

        if (validation.success) {
          completedSteps.push({ step, result })
          continue
        }

        const recovery = await this.attemptRecovery(
          client,
          step,
          result,
          validation.reason,
          userRequest
        )
        if (recovery.success) {
          completedSteps.push({ step, result: recovery.result })
          logs.push({
            timestamp: new Date().toISOString(),
            tool: recovery.action ?? "recovery",
            parameters: recovery.params ?? {},
            result: recovery.result,
          })
          continue
        }

        failedSteps.push({ step, error: validation.reason })
        return { success: false, completedSteps, failedSteps, logs }
      }

      // Fetch final state for reporting
      try {
        const finalState = await client.execute({ type: "get_scene_info" })
        logs.push({
          timestamp: new Date().toISOString(),
          tool: "get_scene_info",
          parameters: {},
          result: finalState,
        })
        return { success: true, completedSteps, failedSteps, finalSceneState: finalState, logs }
      } catch {
        return { success: true, completedSteps, failedSteps, logs }
      }
    } finally {
      await client.close().catch(() => undefined)
    }
  }

  private async validateStep(step: PlanStep, result: unknown, userRequest: string) {
    const prompt = `User goal: ${userRequest}

Step executed:
- Action: ${step.action}
- Parameters: ${JSON.stringify(step.parameters)}
- Expected outcome: ${step.expectedOutcome}

Tool result:
${JSON.stringify(result, null, 2)}

${VALIDATION_OUTPUT_FORMAT}`

    const response = await generateGeminiResponse({
      messages: [{ role: "user", content: prompt }],
      temperature: 0.0,
      topP: 0.1,
      topK: 1,
      maxOutputTokens: 256,
      systemPrompt: VALIDATION_SYSTEM_PROMPT,
    })

    const parsed = this.parseJson(response.text)
    const success = Boolean(parsed?.success)
    const reason = typeof parsed?.reason === "string" ? parsed.reason : "Validation failed"

    return {
      success,
      reason,
      concerns: Array.isArray(parsed?.concerns) ? parsed.concerns : [],
    }
  }

  private async attemptRecovery(
    client: ReturnType<typeof createMcpClient>,
    step: PlanStep,
    result: unknown,
    reason: string,
    userRequest: string
  ): Promise<{ success: boolean; action?: string; params?: Record<string, unknown>; result?: unknown }> {
    const prompt = `A Blender MCP command failed.

User goal: ${userRequest}
Failed step: ${step.action} with params ${JSON.stringify(step.parameters)}
Failure reason: ${reason}
Tool result: ${JSON.stringify(result, null, 2)}

Suggest exactly one recovery action if feasible.
${RECOVERY_OUTPUT_FORMAT}`

    const response = await generateGeminiResponse({
      messages: [{ role: "user", content: prompt }],
      temperature: 0.4,
      topP: 0.8,
      maxOutputTokens: 256,
      systemPrompt: RECOVERY_SYSTEM_PROMPT,
    })

    const parsed = this.parseJson(response.text)
    const action = typeof parsed?.recovery_action === "string" ? parsed.recovery_action : null
    const params = parsed?.recovery_params && typeof parsed.recovery_params === "object" ? parsed.recovery_params : {}

    if (!action) {
      return { success: false }
    }

    try {
      const recoveryResult = await client.execute({ type: action, params })
      return { success: true, action, params, result: recoveryResult }
    } catch (error) {
      return {
        success: false,
        action,
        params,
        result: error instanceof Error ? error.message : "Recovery failed",
      }
    }
  }

  private parseJson(raw: string): Record<string, unknown> | null {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) return null
    try {
      return JSON.parse(match[0])
    } catch {
      return null
    }
  }
}
