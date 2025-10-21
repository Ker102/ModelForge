import { NextResponse } from "next/server"
import { z } from "zod"
import { createMcpClient } from "@/lib/mcp"

const commandSchema = z.object({
  type: z.string().min(1, "Command type is required"),
  params: z.record(z.any()).optional(),
})

export async function POST(req: Request) {
  const client = createMcpClient()

  try {
    const body = await req.json()
    const { type, params } = commandSchema.parse(body)
    const response = await client.execute({
      type,
      params,
    })

    return NextResponse.json({ response })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: "Invalid command payload",
          details: error.flatten(),
        },
        { status: 400 }
      )
    }

    console.error("MCP command execution failed:", error)
    return NextResponse.json(
      {
        error:
          error instanceof Error ? error.message : "Failed to execute MCP command",
      },
      { status: 500 }
    )
  } finally {
    await client.close().catch(() => {
      // ignore close errors
    })
  }
}
