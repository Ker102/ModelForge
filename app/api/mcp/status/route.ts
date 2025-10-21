import { NextResponse } from "next/server"
import { getMcpConfig } from "@/lib/mcp"
import { checkMcpConnection } from "@/lib/mcp/client"

export async function GET() {
  try {
    const config = getMcpConfig()
    const status = await checkMcpConnection()

    return NextResponse.json({
      config,
      status,
    })
  } catch (error) {
    console.error("MCP status check failed:", error)
    return NextResponse.json(
      {
        error: "Unable to read MCP configuration",
      },
      { status: 500 }
    )
  }
}
