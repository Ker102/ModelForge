"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { cn } from "@/lib/utils"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AdvisorMessage {
    id: string
    role: "user" | "advisor"
    content: string
    timestamp: string
}

interface StudioAdvisorProps {
    projectId: string
    /** Current workflow context for smart recommendations */
    workflowContext?: {
        currentStep?: string
        completedSteps?: string[]
        lastError?: string
    }
    className?: string
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function StudioAdvisor({
    projectId,
    workflowContext,
    className,
}: StudioAdvisorProps) {
    const [messages, setMessages] = useState<AdvisorMessage[]>([
        {
            id: "welcome",
            role: "advisor",
            content:
                "👋 Hi! I'm your ModelForge assistant. I can help you choose the right tools, explain concepts, troubleshoot errors, or suggest next steps. Ask me anything!",
            timestamp: new Date().toISOString(),
        },
    ])
    const [input, setInput] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const [isExpanded, setIsExpanded] = useState(true)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    const handleSend = useCallback(
        async (e: React.FormEvent) => {
            e.preventDefault()
            const trimmed = input.trim()
            if (!trimmed || isLoading) return

            const userMsg: AdvisorMessage = {
                id: `user-${Date.now()}`,
                role: "user",
                content: trimmed,
                timestamp: new Date().toISOString(),
            }

            setMessages((prev) => [...prev, userMsg])
            setInput("")
            setIsLoading(true)

            try {
                const res = await fetch("/api/ai/advisor", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        projectId,
                        message: trimmed,
                        workflowContext,
                    }),
                })

                if (!res.ok) throw new Error("Advisor request failed")

                const data = await res.json()

                const advisorMsg: AdvisorMessage = {
                    id: `advisor-${Date.now()}`,
                    role: "advisor",
                    content: data.response ?? "I'm not sure about that. Could you rephrase?",
                    timestamp: new Date().toISOString(),
                }

                setMessages((prev) => [...prev, advisorMsg])
            } catch {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: `error-${Date.now()}`,
                        role: "advisor",
                        content: "Sorry, I couldn't process that. Please try again.",
                        timestamp: new Date().toISOString(),
                    },
                ])
            } finally {
                setIsLoading(false)
            }
        },
        [input, isLoading, projectId, workflowContext]
    )

    if (!isExpanded) {
        return (
            <button
                type="button"
                onClick={() => setIsExpanded(true)}
                className={cn(
                    "flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border/60 bg-card/80 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-card transition-all shadow-sm",
                    className
                )}
            >
                <span className="text-lg">💬</span>
                <span>Assistant</span>
                {messages.length > 1 && (
                    <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-violet-500/20 text-violet-400">
                        {messages.length - 1}
                    </span>
                )}
            </button>
        )
    }

    return (
        <div
            className={cn(
                "flex flex-col rounded-xl border border-border/60 bg-card/80 shadow-sm overflow-hidden",
                className
            )}
        >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-border/40 bg-gradient-to-r from-violet-500/5 to-purple-500/5">
                <div className="flex items-center gap-2">
                    <span className="text-sm">💬</span>
                    <span className="text-sm font-medium text-foreground">Assistant</span>
                    <span className="text-[10px] text-muted-foreground/60 px-1.5 py-0.5 rounded bg-muted/50">
                        Advisory only
                    </span>
                </div>
                <button
                    type="button"
                    onClick={() => setIsExpanded(false)}
                    className="text-muted-foreground hover:text-foreground text-xs transition-colors"
                >
                    ▼ Minimize
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 max-h-[280px] min-h-[120px]">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={cn(
                            "flex",
                            msg.role === "user" ? "justify-end" : "justify-start"
                        )}
                    >
                        <div
                            className={cn(
                                "max-w-[85%] rounded-lg px-3 py-2 text-sm",
                                msg.role === "user"
                                    ? "bg-violet-500/20 text-foreground"
                                    : "bg-muted/40 text-foreground/90"
                            )}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-muted/40 rounded-lg px-3 py-2 text-sm text-muted-foreground">
                            <span className="animate-pulse">Thinking...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="border-t border-border/40 p-3 flex gap-2">
                <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about tools, concepts, or get suggestions..."
                    disabled={isLoading}
                    className="flex-1 rounded-lg border border-border/60 bg-background/80 px-3 py-2 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50 disabled:opacity-50"
                />
                <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className={cn(
                        "px-3 py-2 rounded-lg text-sm font-medium transition-all",
                        input.trim() && !isLoading
                            ? "bg-violet-600 text-white hover:bg-violet-500"
                            : "bg-muted/50 text-muted-foreground cursor-not-allowed"
                    )}
                >
                    Ask
                </button>
            </form>

            {/* Suggestion chips */}
            <div className="px-3 pb-3 flex flex-wrap gap-1.5">
                {[
                    "What tool should I use next?",
                    "What is UV unwrapping?",
                    "How do I make it look realistic?",
                ].map((suggestion) => (
                    <button
                        key={suggestion}
                        type="button"
                        onClick={() => {
                            setInput(suggestion)
                            inputRef.current?.focus()
                        }}
                        className="px-2.5 py-1 rounded-full text-[11px] border border-border/40 text-muted-foreground/70 hover:text-foreground hover:border-violet-500/40 hover:bg-violet-500/5 transition-colors"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </div>
    )
}
