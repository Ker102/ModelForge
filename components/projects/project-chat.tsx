"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { UsageSummary } from "@/lib/usage"

interface CommandStub {
  id: string
  tool: string
  description: string
  status: "pending" | "ready" | "executed" | "failed"
  confidence: number
  arguments?: Record<string, unknown>
  notes?: string
  result?: unknown
  error?: string
}

interface ChatMessage {
  id?: string
  role: "user" | "assistant"
  content: string
  createdAt?: string
  mcpCommands?: CommandStub[]
}

type ConversationHistoryItem = {
  id: string
  lastMessageAt: string
  preview?: string
  messages: ChatMessage[]
}

interface ProjectChatProps {
  projectId: string
  initialConversation?: {
    id: string
    messages: ChatMessage[]
  } | null
  initialUsage?: UsageSummary
  conversationHistory?: ConversationHistoryItem[]
}

export function ProjectChat({
  projectId,
  initialConversation,
  initialUsage,
  conversationHistory,
}: ProjectChatProps) {
  const router = useRouter()
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversation?.id ?? null
  )
  const [messages, setMessages] = useState<ChatMessage[]>(
    initialConversation?.messages ?? []
  )
  const [history, setHistory] = useState<ConversationHistoryItem[]>(
    conversationHistory ?? []
  )
  const [usage, setUsage] = useState<UsageSummary | undefined>(initialUsage)
  const [input, setInput] = useState("")
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSend = input.trim().length > 0 && !isSending

  const formattedUsage = useMemo(() => {
    if (!usage) return null
    return {
      daily: usage.daily.limit
        ? `${usage.daily.used} / ${usage.daily.limit}`
        : `${usage.daily.used} used`,
      monthly: usage.monthly.limit
        ? `${usage.monthly.used} / ${usage.monthly.limit}`
        : `${usage.monthly.used} used`,
    }
  }, [usage])

  useEffect(() => {
    setHistory(conversationHistory ?? [])
  }, [conversationHistory])

  useEffect(() => {
    if (initialConversation?.id && initialConversation.id !== conversationId) {
      setConversationId(initialConversation.id)
      setMessages(initialConversation.messages.map((msg) => ({ ...msg })))
      return
    }

    if (!initialConversation?.id && conversationId && history.length === 0) {
      setConversationId(null)
      setMessages([])
    }
  }, [initialConversation, conversationId, history])

  const renderStatusBadge = (status: CommandStub["status"]) => {
    const variantMap: Record<CommandStub["status"], { variant: "default" | "secondary" | "outline" | "destructive"; label: string }> = {
      pending: { variant: "outline", label: "Pending" },
      ready: { variant: "secondary", label: "Ready" },
      executed: { variant: "default", label: "Executed" },
      failed: { variant: "destructive", label: "Failed" },
    }
    const { variant, label } = variantMap[status]
    return (
      <Badge variant={variant} className="uppercase text-[10px] tracking-wide">
        {label}
      </Badge>
    )
  }

  const formatResult = (value: unknown) => {
    if (value === undefined || value === null) return null
    if (typeof value === "string") return value
    try {
      return JSON.stringify(value, null, 2)
    } catch {
      return String(value)
    }
  }

  const formatHistoryLabel = (timestamp: string) =>
    new Date(timestamp).toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })

  const isViewingHistory = useMemo(() => {
    if (!conversationId) {
      return false
    }
    return history.some((item) => item.id === conversationId)
  }, [conversationId, history])

  function handleLoadConversation(conversation: ConversationHistoryItem) {
    setConversationId(conversation.id)
    setMessages(conversation.messages.map((msg) => ({ ...msg })))
    setError(null)
    setInput("")
    setIsSending(false)
  }

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    if (!canSend) return

    const trimmed = input.trim()
    const now = new Date().toISOString()
    const tempUserId = `temp-user-${Date.now()}`
    const tempAssistantId = `temp-assistant-${Date.now()}`

    setIsSending(true)
    setError(null)
    setInput("")
    setMessages((prev) => [
      ...prev,
      {
        id: tempUserId,
        role: "user",
        content: trimmed,
        createdAt: now,
      },
      {
        id: tempAssistantId,
        role: "assistant",
        content: "",
        createdAt: now,
        mcpCommands: [],
      },
    ])

    try {
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          projectId,
          conversationId: conversationId ?? undefined,
          startNew: !conversationId,
          message: trimmed,
        }),
      })

      if (!response.ok || !response.body) {
        let data: Record<string, unknown> | null = null
        try {
          data = (await response.json()) as Record<string, unknown>
        } catch {
          data = null
        }
        const errorMessage =
          typeof data?.error === "string" ? data.error : "Failed to send message"
        setError(errorMessage)
        const usagePayload = data?.usage as UsageSummary | undefined
        if (usagePayload) {
          setUsage(usagePayload)
        }
        setMessages((prev) =>
          prev.filter((msg) => msg.id !== tempAssistantId)
        )
        return
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let assistantContent = ""
      let streamFinished = false

      while (!streamFinished) {
        const { done, value } = await reader.read()
        if (done) {
          streamFinished = true
        }
        buffer += decoder.decode(value ?? new Uint8Array(), {
          stream: !done,
        })

        let newlineIndex: number
        while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
          const line = buffer.slice(0, newlineIndex).trim()
          buffer = buffer.slice(newlineIndex + 1)

          if (!line) {
            continue
          }

          let event: Record<string, unknown>
          try {
            event = JSON.parse(line) as Record<string, unknown>
          } catch {
            continue
          }

          const eventType = typeof event.type === "string" ? event.type : undefined
          if (!eventType) {
            continue
          }

          switch (eventType) {
            case "init": {
              const incomingConversationId =
                typeof event.conversationId === "string"
                  ? event.conversationId
                  : undefined
              if (incomingConversationId) {
                setConversationId(incomingConversationId)
              }
              break
            }
            case "delta": {
              const delta = typeof event.delta === "string" ? event.delta : ""
              assistantContent += delta
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === tempAssistantId
                    ? { ...msg, content: assistantContent }
                    : msg
                )
              )
              break
            }
            case "usage": {
              const usagePayload = event.usage as UsageSummary | undefined
              if (usagePayload) {
                setUsage(usagePayload)
              }
              break
            }
            case "complete": {
              const messagesPayload = Array.isArray(event.messages)
                ? (event.messages as Array<Record<string, unknown>>)
                : []
              const userRecordRaw = messagesPayload[0]
              const assistantRecordRaw = messagesPayload[1]
              const suggestionPayload = Array.isArray(event.commandSuggestions)
                ? (event.commandSuggestions as CommandStub[])
                : undefined

              const completedConversationId =
                typeof event.conversationId === "string"
                  ? event.conversationId
                  : undefined
              if (completedConversationId) {
                setConversationId(completedConversationId)
              }

              if (userRecordRaw) {
                const userRecord = userRecordRaw as ChatMessage
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === tempUserId
                      ? {
                          ...msg,
                          id: userRecord.id ?? msg.id,
                          createdAt: userRecord.createdAt ?? msg.createdAt,
                        }
                      : msg
                  )
                )
              }

              let assistantRecordId: string | undefined
              if (assistantRecordRaw) {
                const assistantRecord = assistantRecordRaw as ChatMessage & {
                  mcpCommands?: CommandStub[]
                }
                assistantContent =
                  assistantRecord.content ?? assistantContent
                assistantRecordId = assistantRecord.id
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === tempAssistantId
                      ? {
                          ...msg,
                          id: assistantRecord.id ?? msg.id,
                          content:
                            assistantRecord.content ?? assistantContent,
                          createdAt:
                            assistantRecord.createdAt ?? msg.createdAt,
                          mcpCommands:
                            assistantRecord.mcpCommands?.length
                              ? assistantRecord.mcpCommands
                              : suggestionPayload,
                        }
                      : msg
                  )
                )
              }

              const usagePayload = event.usage as UsageSummary | undefined
              if (usagePayload) {
                setUsage(usagePayload)
              }

              if (suggestionPayload && completedConversationId) {
                setHistory((prev) =>
                  prev.map((item) =>
                    item.id === completedConversationId
                      ? {
                          ...item,
                          messages: item.messages.map((msg) =>
                            assistantRecordId && msg.id === assistantRecordId
                              ? {
                                  ...msg,
                                  mcpCommands: suggestionPayload,
                                }
                              : msg
                          ),
                        }
                      : item
                  )
                )
              }

              router.refresh()
              streamFinished = true
              break
            }
            case "error": {
              const errorMessage =
                typeof event.error === "string"
                  ? event.error
                  : "Failed to process AI request"
              setError(errorMessage)
              setMessages((prev) =>
                prev.filter((msg) => msg.id !== tempAssistantId)
              )
              streamFinished = true
              break
            }
            default:
              break
          }
        }
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Try again."
      )
      setMessages((prev) =>
        prev.filter((msg) => msg.id !== tempAssistantId)
      )
    } finally {
      setIsSending(false)
    }
  }

  function handleStartNew() {
    setConversationId(null)
    setMessages([])
    setError(null)
    setInput("")
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle>ModelForge Assistant</CardTitle>
            {isViewingHistory && (
              <Badge variant="outline" className="uppercase text-[10px]">
                History
              </Badge>
            )}
          </div>
          <CardDescription>
            Ask questions about your Blender project or request AI-powered changes.
          </CardDescription>
        </div>
        {formattedUsage && (
          <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground">
            <Badge variant="secondary" className="uppercase tracking-wide">
              Usage
            </Badge>
            <p>Daily: {formattedUsage.daily}</p>
            <p>Monthly: {formattedUsage.monthly}</p>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {history && history.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span className="font-semibold uppercase tracking-wide text-[11px]">
              Past sessions
            </span>
            {history.map((item) => {
              const isActive = conversationId === item.id
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleLoadConversation(item)}
                  title={item.preview ?? "Open conversation"}
                >
                  {formatHistoryLabel(item.lastMessageAt)}
                </Button>
              )
            })}
          </div>
        )}
        <div className="h-72 overflow-y-auto rounded-md border bg-muted/30 p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-sm text-muted-foreground">
              Start a conversation to plan, modify, or debug your Blender scene.
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={`${message.id ?? index}-${message.role}-${index}`}
                className={`flex flex-col gap-1 ${
                  message.role === "assistant" ? "items-start" : "items-end"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-md px-3 py-2 text-sm ${
                    message.role === "assistant"
                      ? "bg-white shadow"
                      : "bg-primary text-primary-foreground"
                  }`}
                >
                  {message.content}
                </div>
                {message.role === "assistant" &&
                  Array.isArray(message.mcpCommands) &&
                  message.mcpCommands.length > 0 && (
                    <div className="max-w-[80%] rounded-md border border-primary/30 bg-primary/5 px-3 py-2 text-xs text-muted-foreground space-y-2">
                      <p className="font-medium text-primary">
                        MCP execution summary
                      </p>
                      <ul className="space-y-2">
                        {message.mcpCommands.map((command) => (
                          <li key={command.id} className="flex flex-col gap-1 rounded-md border border-border/60 bg-background/70 p-2 text-xs">
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-medium text-foreground">{command.tool}</span>
                              {renderStatusBadge(command.status)}
                            </div>
                            <span className="text-muted-foreground">{command.description}</span>
                            {command.notes && (
                              <span className="italic text-[11px] text-muted-foreground/80">
                                {command.notes}
                              </span>
                            )}
                            {command.status === "failed" && command.error && (
                              <div className="rounded border border-destructive/40 bg-destructive/10 px-2 py-1 text-[11px] text-destructive">
                                {command.error}
                              </div>
                            )}
                            {command.status === "executed" && formatResult(command.result) && (
                              <pre className="rounded bg-muted/60 px-2 py-1 text-[11px] text-muted-foreground whitespace-pre-wrap break-words">
                                {formatResult(command.result)}
                              </pre>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                {message.createdAt && (
                  <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
                    {new Date(message.createdAt).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                )}
              </div>
            ))
          )}
        </div>
        {error && (
          <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        )}
        <form onSubmit={handleSend} className="space-y-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe what you need—ModelForge can craft Blender geometry, tweak materials, set up lighting, and more."
            rows={3}
            disabled={isSending}
            className={cn(
              "flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
              "resize-none"
            )}
          />
          <div className="flex items-center justify-between gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={handleStartNew}
              disabled={isSending || messages.length === 0}
            >
              Start New Conversation
            </Button>
            <Button type="submit" disabled={!canSend}>
              {isSending ? "Thinking..." : "Send to ModelForge"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
