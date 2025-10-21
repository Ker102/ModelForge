"use server"

import net from "net"
import { randomUUID } from "crypto"
import { getMcpConfig } from "./config"
import { McpCommand, McpResponse } from "./types"

export class BlenderMcpClient {
  private socket: net.Socket | null = null
  private connected = false

  constructor(private readonly config = getMcpConfig()) {}

  /**
   * Establish a socket connection to the Blender MCP server.
   * Connection is memoized per client instance.
   */
  private async ensureConnection() {
    if (this.connected && this.socket) {
      return this.socket
    }

    const { host, port, timeoutMs } = this.config

    this.socket = await new Promise<net.Socket>((resolve, reject) => {
      const socket = net.createConnection({ host, port }, () => {
        this.connected = true
        resolve(socket)
      })

      socket.setTimeout(timeoutMs, () => {
        socket.destroy(new Error("Blender MCP connection timed out"))
      })

      socket.once("error", (error) => {
        reject(error)
      })
    })

    this.socket.on("close", () => {
      this.connected = false
      this.socket = null
    })

    return this.socket
  }

  /**
   * Send a command to the Blender MCP server.
   * NOTE: The final implementation will include structured payloads and response parsing.
   */
  async execute<T = unknown>(command: McpCommand): Promise<McpResponse<T>> {
    const socket = await this.ensureConnection()

    const payload = JSON.stringify({
      ...command,
      id: command.id ?? randomUUID(),
    })

    const response = await new Promise<string>((resolve, reject) => {
      const chunks: Buffer[] = []

      const onData = (chunk: Buffer) => {
        chunks.push(chunk)
        if (chunk.toString().trim().endsWith("}")) {
          cleanup()
          resolve(Buffer.concat(chunks).toString("utf8"))
        }
      }

      const onError = (error: Error) => {
        cleanup()
        reject(error)
      }

      const onTimeout = () => {
        cleanup()
        reject(new Error("Timed out while waiting for Blender MCP response"))
      }

      const cleanup = () => {
        socket.off("data", onData)
        socket.off("error", onError)
        socket.off("timeout", onTimeout)
      }

      socket.once("error", onError)
      socket.once("timeout", onTimeout)
      socket.on("data", onData)
      socket.write(`${payload}\n`)
    })

    try {
      const parsed = JSON.parse(response) as McpResponse<T>
      return {
        ...parsed,
        raw: parsed.raw ?? response,
      }
    } catch {
      return {
        status: "error",
        message: "Failed to parse Blender MCP response",
        raw: response,
      }
    }
  }

  async close() {
    if (!this.socket) return
    await new Promise<void>((resolve) => {
      this.socket?.end(() => {
        resolve()
      })
    })
    this.socket.destroy()
    this.connected = false
    this.socket = null
  }
}

export function createMcpClient() {
  return new BlenderMcpClient()
}
