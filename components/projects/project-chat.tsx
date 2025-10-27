"use client"

import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { UsageSummary } from "@/lib/usage"
import type { PlanningMetadata, PlanStep } from "@/lib/orchestration/types"
import { parsePlanningMetadata } from "@/lib/orchestration/plan-utils"
import { ImagePlus, X } from "lucide-react"

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
  plan?: PlanningMetadata
  attachments?: ChatAttachment[]
}

type ConversationHistoryItem = {
  id: string
  lastMessageAt: string
  preview?: string
  messages: ChatMessage[]
}

interface ChatAttachment {
  id?: string
  name: string
  type: string
  size?: number
  url?: string
  previewUrl?: string
}

interface PendingAttachment {
  id: string
  name: string
  size: number
  type: string
  dataUrl: string
  base64: string
}

interface ProjectChatProps {
  projectId: string
  initialConversation?: {
    id: string
    messages: ChatMessage[]
  } | null
  initialUsage?: UsageSummary
  conversationHistory?: ConversationHistoryItem[]
  initialAssetConfig: {
    allowHyper3d: boolean
    allowSketchfab: boolean
    allowPolyHaven: boolean
  }
}

export function ProjectChat({
  projectId,
  initialConversation,
  initialUsage,
  conversationHistory,
  initialAssetConfig,
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
  const [assetConfig, setAssetConfig] = useState(initialAssetConfig)
  const [attachments, setAttachments] = useState<PendingAttachment[]>([])
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024
  const MAX_ATTACHMENTS = 4

  const canSend = (input.trim().length > 0 || attachments.length > 0) && !isSending

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

  const resolveCommandForStep = (
    step: PlanStep,
    index: number,
    commands?: CommandStub[]
  ) => {
    if (!commands?.length) return null
    return commands[index] ?? commands.find((command) => command.tool === step.action) ?? null
  }

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
  setAttachments([])
}

const handleAttachmentButton = () => {
  fileInputRef.current?.click()
}

const readFileAsDataUrl = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })

const handleFileInputChange = async (event: ChangeEvent<HTMLInputElement>) => {
  const files = event.target.files
  if (!files || files.length === 0) {
    return
  }

  const remainingSlots = MAX_ATTACHMENTS - attachments.length
  if (remainingSlots <= 0) {
    setError(`You can attach up to ${MAX_ATTACHMENTS} images per message.`)
    event.target.value = ""
    return
  }

  const selectedFiles = Array.from(files).slice(0, remainingSlots)
  const newAttachments: PendingAttachment[] = []

  for (const file of selectedFiles) {
    if (!file.type.startsWith("image/")) {
      setError("Only image files are supported right now.")
      continue
    }
    if (file.size > MAX_ATTACHMENT_SIZE) {
      setError("Images must be 5MB or smaller.")
      continue
    }

    try {
      const dataUrl = await readFileAsDataUrl(file)
      const base64 = dataUrl.split(",")[1] ?? ""
      newAttachments.push({
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        type: file.type,
        dataUrl,
        base64,
      })
    } catch (fileError) {
      console.error(fileError)
      setError("Failed to read one of the files. Please try again.")
    }
  }

  if (newAttachments.length > 0) {
    setAttachments((prev) => [...prev, ...newAttachments])
    setError(null)
  }

  event.target.value = ""
}

const handleRemoveAttachment = (id: string) => {
  setAttachments((prev) => prev.filter((attachment) => attachment.id !== id))
}

async function handleSend(e: React.FormEvent) {
    e.preventDefault()
    if (!canSend) return

    const trimmed = input.trim()
    const now = new Date().toISOString()
    const tempUserId = `temp-user-${Date.now()}`
    const tempAssistantId = `temp-assistant-${Date.now()}`
    const draftAttachments: ChatAttachment[] = attachments.map((attachment) => ({
      id: attachment.id,
      name: attachment.name,
      type: attachment.type,
      size: attachment.size,
      previewUrl: attachment.dataUrl,
    }))

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
        attachments: draftAttachments,
      },
      {
        id: tempAssistantId,
        role: "assistant",
        content: "",
        createdAt: now,
        mcpCommands: [],
      },
    ])
    setAttachments([])

    try {
      const payload: Record<string, unknown> = {
        projectId,
        conversationId: conversationId ?? undefined,
        startNew: !conversationId,
        message: trimmed,
      }

      if (attachments.length > 0) {
        payload.attachments = attachments.map((attachment) => ({
          id: attachment.id,
          name: attachment.name,
          type: attachment.type,
          size: attachment.size,
          data: attachment.base64,
        }))
      }

      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
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
              const planPayload = parsePlanningMetadata(event.planning)

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
                          plan: planPayload ?? assistantRecord.plan ?? msg.plan,
                        }
                      : msg
                  )
                )
              }

              const usagePayload = event.usage as UsageSummary | undefined
              if (usagePayload) {
                setUsage(usagePayload)
              }

              if ((suggestionPayload || planPayload) && completedConversationId) {
                setHistory((prev) =>
                  prev.map((item) =>
                    item.id === completedConversationId
                      ? {
                          ...item,
                          messages: item.messages.map((msg) =>
                            assistantRecordId && msg.id === assistantRecordId
                              ? {
                                  ...msg,
                                  mcpCommands: suggestionPayload ?? msg.mcpCommands,
                                  plan: planPayload ?? msg.plan,
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
    setAttachments([])
  }

  async function updateAssetConfig(partial: Partial<typeof assetConfig>) {
    setError(null)
    const previousConfig = assetConfig
    const nextConfig = { ...assetConfig, ...partial }
    setAssetConfig(nextConfig)
    try {
      const response = await fetch(`/api/projects/${projectId}/settings`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          allowHyper3dAssets: nextConfig.allowHyper3d,
          allowSketchfabAssets: nextConfig.allowSketchfab,
          allowPolyHavenAssets: nextConfig.allowPolyHaven,
        }),
      })
      if (!response.ok) {
        throw new Error("Failed to update asset preferences")
      }
      const data = (await response.json()) as {
        allowHyper3dAssets?: boolean
        allowSketchfabAssets?: boolean
        allowPolyHavenAssets?: boolean
      }
      setAssetConfig({
        allowHyper3d: Boolean(data.allowHyper3dAssets),
        allowSketchfab: Boolean(data.allowSketchfabAssets),
        allowPolyHaven: data.allowPolyHavenAssets !== false,
      })
    } catch (err) {
      console.error(err)
      setAssetConfig(previousConfig)
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update asset preferences right now."
      )
    }
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
        <div className="rounded-md border border-border/60 bg-muted/40 p-4 space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="font-semibold text-sm">Asset integrations</p>
              <p className="text-xs text-muted-foreground">
                Poly Haven works out of the box. Enable Hyper3D or Sketchfab only after adding their API keys in the Blender add-on.
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4"
                checked={assetConfig.allowPolyHaven}
                onChange={(event) =>
                  updateAssetConfig({ allowPolyHaven: event.target.checked })
                }
              />
              <span>
                <span className="font-medium text-foreground">Use Poly Haven assets</span>
                <span className="block text-xs text-muted-foreground">
                  Enabled by default. Provides HDRIs, textures, and models that do not require API keys.
                  Disable if you prefer to manage downloads manually.
                </span>
              </span>
            </label>
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4"
                checked={assetConfig.allowHyper3d}
                onChange={(event) =>
                  updateAssetConfig({ allowHyper3d: event.target.checked })
                }
              />
              <span>
                <span className="font-medium text-foreground">Use Hyper3D Rodin assets</span>
                <span className="block text-xs text-muted-foreground">
                  Requires Hyper3D credentials in Blender. When disabled, the planner will avoid Hyper3D commands.
                </span>
              </span>
            </label>
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4"
                checked={assetConfig.allowSketchfab}
                onChange={(event) =>
                  updateAssetConfig({ allowSketchfab: event.target.checked })
                }
              />
              <span>
                <span className="font-medium text-foreground">Use Sketchfab assets</span>
                <span className="block text-xs text-muted-foreground">
                  Requires Sketchfab API token in Blender. When disabled, the planner skips Sketchfab search/download.
                </span>
              </span>
            </label>
          </div>
        </div>
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
                {message.attachments?.length ? (
                  <div
                    className={`flex flex-wrap gap-2 ${
                      message.role === "assistant" ? "justify-start" : "justify-end"
                    }`}
                  >
                    {message.attachments.map((attachment) => {
                      const previewSrc = attachment.previewUrl ?? attachment.url
                      if (!previewSrc) return null
                      const key = attachment.id ?? `${attachment.name}-${previewSrc}`
                      return (
                        <a
                          key={key}
                          href={attachment.url ?? previewSrc}
                          target={attachment.url ? "_blank" : undefined}
                          rel={attachment.url ? "noreferrer" : undefined}
                          className="block h-20 w-20 overflow-hidden rounded-md border border-border/60 bg-background"
                        >
                          <Image
                            src={previewSrc}
                            alt={attachment.name ?? "Attachment"}
                            width={80}
                            height={80}
                            unoptimized
                            className="h-full w-full object-cover"
                          />
                        </a>
                      )
                    })}
                  </div>
                ) : null}
                {message.role === "assistant" && message.plan && (
                  <div className="max-w-[80%] rounded-md border border-primary/30 bg-primary/5 px-3 py-2 text-xs text-muted-foreground space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-primary">Planning summary</span>
                      <div className="flex items-center gap-1">
                        <Badge
                          variant={message.plan.executionSuccess ? "default" : "destructive"}
                          className="uppercase text-[10px]"
                        >
                          {message.plan.executionSuccess ? "Plan executed" : "Plan incomplete"}
                        </Badge>
                        {message.plan.fallbackUsed && (
                          <Badge variant="outline" className="uppercase text-[10px]">
                            Fallback used
                          </Badge>
                        )}
                        {message.plan.retries > 0 && (
                          <Badge variant="secondary" className="uppercase text-[10px]">
                            Retries: {message.plan.retries}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <p className="text-muted-foreground">{message.plan.planSummary}</p>
                    {message.plan.analysis && (
                      <div className="rounded bg-background/70 px-2 py-1 text-[11px] text-muted-foreground space-y-1">
                        <p className="font-semibold text-foreground">Component breakdown</p>
                        <ul className="list-disc pl-4">
                          {message.plan.analysis.components.map((component) => (
                            <li key={component}>{component}</li>
                          ))}
                        </ul>
                        {message.plan.analysis.materialGuidelines.length > 0 && (
                          <div>
                            <p className="font-medium text-foreground mt-1">Material guidelines</p>
                            <ul className="list-disc pl-4">
                              {message.plan.analysis.materialGuidelines.map((guideline) => (
                                <li key={guideline}>{guideline}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <div className="flex flex-wrap gap-2 text-[10px] uppercase tracking-wide">
                          {typeof message.plan.analysis.minimumMeshObjects === "number" && (
                            <Badge variant="outline">
                              Min meshes: {message.plan.analysis.minimumMeshObjects}
                            </Badge>
                          )}
                          {message.plan.analysis.requireLighting !== false && (
                            <Badge variant="outline">Lighting required</Badge>
                          )}
                          {message.plan.analysis.requireCamera !== false && (
                            <Badge variant="outline">Camera required</Badge>
                          )}
                        </div>
                        {message.plan.analysis.notes?.length ? (
                          <div className="mt-1 text-muted-foreground">
                            <p className="font-medium text-foreground">Notes</p>
                            <ul className="list-disc pl-4">
                              {message.plan.analysis.notes.map((note) => (
                                <li key={note}>{note}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null}
                      </div>
                    )}
                    {message.plan.sceneSnapshot && (
                      <details className="rounded bg-background/70 px-2 py-1 text-[11px] text-muted-foreground">
                        <summary className="cursor-pointer text-primary">Scene snapshot used</summary>
                        <pre className="mt-1 whitespace-pre-wrap break-words text-[11px]">
                          {message.plan.sceneSnapshot}
                        </pre>
                      </details>
                    )}
                    <div className="space-y-2">
                      {message.plan.planSteps.map((step, stepIndex) => {
                        const commandForStep = resolveCommandForStep(step, stepIndex, message.mcpCommands)
                        const inferredStatus: CommandStub["status"] = commandForStep?.status
                          ?? (message.plan.executionSuccess ? "executed" : "failed")
                        return (
                          <div
                            key={`${step.stepNumber}-${step.action}-${stepIndex}`}
                            className="rounded-md border border-border/60 bg-background px-2 py-1"
                          >
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-medium text-foreground">
                                Step {step.stepNumber}: {step.action}
                              </span>
                              {renderStatusBadge(inferredStatus)}
                            </div>
                            {step.rationale && (
                              <p className="text-[11px] text-muted-foreground">
                                {step.rationale}
                              </p>
                            )}
                            {commandForStep?.error && (
                              <div className="mt-1 rounded border border-destructive/30 bg-destructive/10 px-2 py-1 text-[11px] text-destructive">
                                {commandForStep.error}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                    {message.plan.errors?.length ? (
                      <div className="rounded border border-destructive/40 bg-destructive/10 px-2 py-1 text-[11px] text-destructive">
                        {message.plan.errors.join("; ")}
                      </div>
                    ) : null}
                  </div>
                )}
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
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={handleFileInputChange}
          />
          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-3">
              {attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className="relative h-20 w-20 overflow-hidden rounded-md border border-border/70 bg-background shadow-sm"
                >
                  <Image
                    src={attachment.dataUrl}
                    alt={attachment.name}
                    width={80}
                    height={80}
                    unoptimized
                    className="h-full w-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveAttachment(attachment.id)}
                    className="absolute right-1 top-1 rounded-full bg-background/90 p-1 text-xs text-muted-foreground hover:bg-background"
                    aria-label={`Remove ${attachment.name}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
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
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAttachmentButton}
                disabled={isSending || attachments.length >= MAX_ATTACHMENTS}
              >
                <ImagePlus className="mr-2 h-4 w-4" />
                Attach image
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={handleStartNew}
                disabled={isSending || messages.length === 0}
              >
                Start New Conversation
              </Button>
            </div>
            <Button type="submit" disabled={!canSend}>
              {isSending ? "Thinking..." : "Send to ModelForge"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
