import { randomUUID } from "crypto"
import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import {
  canConsumeAiRequest,
  getUsageSummary,
  logUsage,
} from "@/lib/usage"
import { streamGeminiResponse } from "@/lib/gemini"
import { createMcpClient } from "@/lib/mcp"
import { z } from "zod"

const MAX_HISTORY_MESSAGES = 12

type CommandStatus = "pending" | "ready" | "executed" | "failed"

interface CommandStub {
  id: string
  tool: string
  description: string
  status: CommandStatus
  confidence: number
  arguments: Record<string, unknown>
  notes?: string
}

interface ExecutedCommand extends CommandStub {
  status: "executed" | "failed"
  result?: unknown
  error?: string
}

function createStubId() {
  try {
    return randomUUID()
  } catch {
    return `stub-${Date.now()}`
  }
}

function buildCommandStubs(prompt: string): CommandStub[] {
  const lowerPrompt = prompt.toLowerCase()
  const promptSnippet = prompt.slice(0, 200)

  const stubs: CommandStub[] = []

  const housePattern = /(house|building|home|structure)/i
  const primitiveMatch = /(cube|sphere|plane|cone|cylinder|torus)/i.exec(lowerPrompt)

  const ensureHelpers = `import bpy

`
    + `def ensure_collection(name):
`
    + `    collection = bpy.data.collections.get(name)
`
    + `    if collection is None:
`
    + `        collection = bpy.data.collections.new(name)
`
    + `        bpy.context.scene.collection.children.link(collection)
`
    + `    return collection

`
    + `def link_object(obj, collection):
`
    + `    for existing in list(obj.users_collection):
`
    + `        if existing != collection:
`
    + `            existing.objects.unlink(obj)
`
    + `    if obj.name not in collection.objects:
`
    + `        collection.objects.link(obj)

`

  if (housePattern.test(lowerPrompt)) {
    const code = ensureHelpers
      + `collection = ensure_collection("ModelForge")
`
      + `for existing in list(collection.objects):
`
      + `    bpy.data.objects.remove(existing, do_unlink=True)

`
      + `bpy.ops.object.select_all(action='DESELECT')
`
      + `bpy.ops.mesh.primitive_cube_add(size=4, location=(0, 0, 1))
`
      + `base = bpy.context.active_object
`
      + `base.name = "House_Base"
`
      + `base.scale[2] = 0.5
`
      + `link_object(base, collection)

`
      + `bpy.ops.mesh.primitive_cone_add(radius1=3.2, radius2=0.2, depth=2.5, location=(0, 0, 2.75))
`
      + `roof = bpy.context.active_object
`
      + `roof.name = "House_Roof"
`
      + `link_object(roof, collection)

`
      + `print("ModelForge: simple house created")
`

    stubs.push({
      id: createStubId(),
      tool: "execute_code",
      description: "Create a simple house with base and roof",
      status: "pending",
      confidence: 0.55,
      arguments: { code },
      notes: "Generated automatically from ModelForge heuristics.",
    })
  } else if (primitiveMatch) {
    const primitive = primitiveMatch[1]
    const primitiveMap: Record<string, string> = {
      cube: "bpy.ops.mesh.primitive_cube_add",
      sphere: "bpy.ops.mesh.primitive_uv_sphere_add",
      plane: "bpy.ops.mesh.primitive_plane_add",
      cone: "bpy.ops.mesh.primitive_cone_add",
      cylinder: "bpy.ops.mesh.primitive_cylinder_add",
      torus: "bpy.ops.mesh.primitive_torus_add",
    }
    const operation = primitiveMap[primitive as keyof typeof primitiveMap] || primitiveMap.cube
    const code = ensureHelpers
      + `collection = ensure_collection("ModelForge")
`
      + `bpy.ops.object.select_all(action='DESELECT')
`
      + `${operation}(location=(0, 0, 0))
`
      + `obj = bpy.context.active_object
`
      + `obj.name = "${primitive.charAt(0).toUpperCase() + primitive.slice(1)}"
`
      + `link_object(obj, collection)

`
      + `print("ModelForge: ${primitive} created")
`

    stubs.push({
      id: createStubId(),
      tool: "execute_code",
      description: `Create a ${primitive} primitive`,
      status: "pending",
      confidence: 0.45,
      arguments: { code },
      notes: "Generated automatically from ModelForge heuristics.",
    })
  } else if (/light|lighting|sunlamp|sun lamp|sunlight|studio/.test(lowerPrompt)) {
    const code = ensureHelpers
      + `collection = ensure_collection("ModelForge")
`
      + `bpy.ops.object.select_all(action='DESELECT')
`
      + `bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
`
      + `light = bpy.context.active_object
`
      + `light.name = "ModelForge_Sun"
`
      + `light.data.energy = 7.0
`
      + `link_object(light, collection)

`
      + `print("ModelForge: lighting setup added")
`

    stubs.push({
      id: createStubId(),
      tool: "execute_code",
      description: "Add a sun light source",
      status: "pending",
      confidence: 0.3,
      arguments: { code },
      notes: "Generated automatically from ModelForge heuristics.",
    })
  }

  if (stubs.length === 0) {
    const placeholderCode = `print("ModelForge placeholder: ${promptSnippet.replace(/"/g, '')}")`
    stubs.push({
      id: createStubId(),
      tool: "execute_code",
      description: "Log prompt for manual planning",
      status: "pending",
      confidence: 0.1,
      arguments: { code: placeholderCode },
      notes: "No direct automation rule matched. Logged prompt for review.",
    })
  }

  return stubs
}

const chatRequestSchema = z.object({
  projectId: z.string().uuid(),
  conversationId: z.string().uuid().optional(),
  startNew: z.boolean().optional(),
  message: z.string().min(1).max(2000),
})

async function ensureConversation({
  projectId,
  userId,
  conversationId,
  startNew,
}: {
  projectId: string
  userId: string
  conversationId?: string
  startNew?: boolean
}) {
  if (conversationId) {
    const conversation = await prisma.conversation.findFirst({
      where: {
        id: conversationId,
        project: {
          id: projectId,
          userId,
          isDeleted: false,
        },
      },
      select: { id: true },
    })

    if (!conversation) {
      throw new Error("Conversation not found")
    }

    return conversationId
  }

  if (!startNew) {
    const existing = await prisma.conversation.findFirst({
      where: {
        project: {
          id: projectId,
          userId,
          isDeleted: false,
        },
      },
      orderBy: {
        lastMessageAt: "desc",
      },
      select: { id: true },
    })

    if (existing) {
      return existing.id
    }
  }

  const conversation = await prisma.conversation.create({
    data: {
      projectId,
    },
    select: { id: true },
  })

  return conversation.id
}

async function executeCommandPlan(commands: CommandStub[]): Promise<ExecutedCommand[]> {
  if (commands.length === 0) {
    return []
  }

  const client = createMcpClient()
  const executed: ExecutedCommand[] = []

  try {
    for (const command of commands) {
      try {
        const response = await client.execute({
          type: command.tool,
          params: command.arguments,
        })

        if (response.status === "ok") {
          executed.push({
            ...command,
            status: "executed",
            result: response.result ?? response.message ?? response.raw,
            error: undefined,
          })
        } else {
          executed.push({
            ...command,
            status: "failed",
            result: response.result ?? response.raw,
            error: response.message ?? "Command returned an error",
          })
        }
      } catch (error) {
        executed.push({
          ...command,
          status: "failed",
          result: undefined,
          error: error instanceof Error ? error.message : "Failed to execute MCP command",
        })
      }
    }
  } finally {
    await client.close().catch(() => {
      // ignore close errors
    })
  }

  return executed
}

export async function POST(req: Request) {
  try {
    const session = await auth()

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await req.json()
    const { projectId, conversationId, startNew, message } =
      chatRequestSchema.parse(body)

    const project = await prisma.project.findFirst({
      where: {
        id: projectId,
        userId: session.user.id,
        isDeleted: false,
      },
      select: { id: true },
    })

    if (!project) {
      return NextResponse.json(
        { error: "Project not found" },
        { status: 404 }
      )
    }

    const quotaCheck = await canConsumeAiRequest(
      session.user.id,
      session.user.subscriptionTier
    )

    if (!quotaCheck.allowed) {
      const limitLabel =
        quotaCheck.limitType === "daily" ? "daily" : "monthly"
      return NextResponse.json(
        {
          error: `AI request limit reached for your ${limitLabel} allotment. Please upgrade your plan or try again later.`,
          usage: quotaCheck.usage,
        },
        { status: 429 }
      )
    }

    let resolvedConversationId: string
    try {
      resolvedConversationId = await ensureConversation({
        projectId,
        userId: session.user.id,
        conversationId,
        startNew,
      })
    } catch {
      return NextResponse.json(
        { error: "Conversation not found" },
        { status: 404 }
      )
    }

    const historyMessages = await prisma.message.findMany({
      where: { conversationId: resolvedConversationId },
      orderBy: { createdAt: "desc" },
      take: Math.max(0, MAX_HISTORY_MESSAGES - 1),
      select: {
        role: true,
        content: true,
      },
    })

    const trimmedHistory = historyMessages
      .reverse()
      .map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: msg.content,
      }))

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        const send = (data: unknown) => {
          controller.enqueue(
            encoder.encode(`${JSON.stringify(data)}\n`)
          )
        }

        send({ type: "init", conversationId: resolvedConversationId })

        let assistantText = ""
        let tokenUsage: { promptTokens?: number | null; responseTokens?: number | null; totalTokens?: number | null } | undefined

        try {
          for await (const chunk of streamGeminiResponse({
            history: trimmedHistory,
            messages: [
              {
                role: "user",
                content: message,
              },
            ],
            maxOutputTokens: 512,
          })) {
            if (chunk.textDelta) {
              assistantText += chunk.textDelta
              send({ type: "delta", delta: chunk.textDelta })
            }
            if (chunk.usage) {
              tokenUsage = chunk.usage
            }
          }

          const commandSuggestions = buildCommandStubs(message)
          const executedCommands = await executeCommandPlan(commandSuggestions)

          const result = await prisma.$transaction(async (tx) => {
            const userMessageRecord = await tx.message.create({
              data: {
                conversationId: resolvedConversationId,
                role: "user",
                content: message,
              },
              select: {
                id: true,
                role: true,
                content: true,
                createdAt: true,
              },
            })

            const assistantMessageRecord = await tx.message.create({
              data: {
                conversationId: resolvedConversationId,
                role: "assistant",
                content: assistantText,
                mcpCommands: executedCommands,
                mcpResults: {
                  tokens: tokenUsage,
                  commands: executedCommands.map((command) => ({
                    id: command.id,
                    tool: command.tool,
                    status: command.status,
                    result: command.result,
                    error: command.error,
                  })),
                },
              },
              select: {
                id: true,
                role: true,
                content: true,
                mcpCommands: true,
                createdAt: true,
              },
            })

            await tx.conversation.update({
              where: { id: resolvedConversationId },
              data: { lastMessageAt: assistantMessageRecord.createdAt },
            })

            return { userMessageRecord, assistantMessageRecord }
          })

          await logUsage({
            userId: session.user.id,
            projectId,
            requestType: "ai_request",
            tokensUsed: tokenUsage?.totalTokens ?? undefined,
          })

          const usage = await getUsageSummary(
            session.user.id,
            session.user.subscriptionTier
          )

          send({
            type: "complete",
            conversationId: resolvedConversationId,
            messages: [result.userMessageRecord, result.assistantMessageRecord],
            usage,
            tokenUsage,
            commandSuggestions: executedCommands,
          })
        } catch (error) {
          console.error("AI chat stream error:", error)
          send({
            type: "error",
            error:
              error instanceof Error
                ? error.message
                : "Failed to process AI request",
          })
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      headers: {
        "Content-Type": "application/x-ndjson",
        "Cache-Control": "no-cache",
      },
    })
  } catch (error) {
    console.error("AI chat error:", error)
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid input data", details: error.flatten() },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to process AI request" },
      { status: 500 }
    )
  }
}
