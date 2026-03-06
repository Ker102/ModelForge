"use client"

import { cn } from "@/lib/utils"

export interface WorkflowTimelineStep {
    id: string
    title: string
    toolName: string
    status: "pending" | "running" | "done" | "failed"
}

interface WorkflowTimelineProps {
    steps: WorkflowTimelineStep[]
    onRemoveStep: (stepId: string) => void
    onRunAll: () => void
}

export function WorkflowTimeline({
    steps,
    onRemoveStep,
    onRunAll,
}: WorkflowTimelineProps) {
    if (steps.length === 0) return null

    return (
        <div
            className="border-t px-6 py-3 flex items-center gap-3 overflow-x-auto"
            style={{
                borderColor: "hsl(var(--forge-border))",
                backgroundColor: "hsl(var(--forge-surface))",
            }}
        >
            <span
                className="text-xs font-semibold uppercase tracking-wider shrink-0"
                style={{ color: "hsl(var(--forge-text-muted))" }}
            >
                Pipeline
            </span>

            <div className="flex items-center gap-1.5 overflow-x-auto">
                {steps.map((step, index) => (
                    <div key={step.id} className="flex items-center gap-1.5 shrink-0">
                        {/* Step pill */}
                        <div
                            className={cn(
                                "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
                                step.status === "done" && "opacity-60 line-through",
                                step.status === "running" && "animate-pulse",
                            )}
                            style={{
                                borderColor:
                                    step.status === "running"
                                        ? "hsl(var(--forge-accent))"
                                        : "hsl(var(--forge-border))",
                                backgroundColor:
                                    step.status === "running"
                                        ? "hsl(var(--forge-accent-subtle))"
                                        : "hsl(var(--forge-surface))",
                                color:
                                    step.status === "running"
                                        ? "hsl(var(--forge-accent))"
                                        : "hsl(var(--forge-text))",
                            }}
                        >
                            {/* Status dot */}
                            <span
                                className="w-1.5 h-1.5 rounded-full shrink-0"
                                style={{
                                    backgroundColor:
                                        step.status === "done"
                                            ? "hsl(var(--forge-accent))"
                                            : step.status === "failed"
                                                ? "hsl(0 84% 60%)"
                                                : step.status === "running"
                                                    ? "hsl(var(--forge-accent))"
                                                    : "hsl(var(--forge-text-subtle))",
                                }}
                            />
                            <span>
                                {index + 1}. {step.title}
                            </span>
                            <button
                                onClick={() => onRemoveStep(step.id)}
                                className="ml-1 opacity-50 hover:opacity-100 transition text-base leading-none"
                                style={{ color: "hsl(var(--forge-text-muted))" }}
                            >
                                ×
                            </button>
                        </div>

                        {/* Connector arrow */}
                        {index < steps.length - 1 && (
                            <svg
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="hsl(var(--forge-text-subtle))"
                                strokeWidth="2"
                                className="shrink-0"
                            >
                                <polyline points="9 18 15 12 9 6" />
                            </svg>
                        )}
                    </div>
                ))}
            </div>

            <div className="flex-1" />

            {/* Run all button */}
            <button
                onClick={onRunAll}
                className="shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold text-white transition hover:opacity-90"
                style={{ backgroundColor: "hsl(var(--forge-accent))" }}
            >
                Run All
            </button>
        </div>
    )
}
