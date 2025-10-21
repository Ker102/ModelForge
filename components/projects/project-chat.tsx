"use client"

import { useState, useMemo } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { UsageSummary } from "@/lib/usage"

interface ChatMessage {
  id?: string
  role: "user" | "assistant"
  content: string
  createdAt?: string
}

interface ProjectChatProps {
  projectId: string
  initialConversation?: {
    id: string
    messages: ChatMessage[]
  } | null
  initialUsage?: UsageSummary
}

export function ProjectChat({
  projectId,
  initialConversation,
  initialUsage,
}: ProjectChatProps) {
  const router = useRouter()
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversation?.id ?? null
  )
  const [messages, setMessages] = useState<ChatMessage[]>(
    initialConversation?.messages ?? []
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

  async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    if (!canSend) return

    setIsSending(true)
    setError(null)

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
          message: input.trim(),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data?.error ?? "Failed to send message")
        if (data?.usage) {
          setUsage(data.usage)
        }
        return
      }

      setConversationId(data.conversationId)
      setMessages((prev) => [
        ...prev,
        ...(Array.isArray(data.messages)
          ? data.messages.map((msg: ChatMessage) => ({
              ...msg,
              createdAt: msg.createdAt ?? new Date().toISOString(),
            }))
          : []),
      ])
      if (data.usage) {
        setUsage(data.usage)
      }
      setInput("")
      router.refresh()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Try again."
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
          <CardTitle>ModelForge Assistant</CardTitle>
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
