"use client"

import { cn } from "@/lib/utils"

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type WorkflowMode = "autopilot" | "studio"

interface ModeSelectorProps {
    mode: WorkflowMode
    onChange: (mode: WorkflowMode) => void
    className?: string
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ModeSelector({ mode, onChange, className }: ModeSelectorProps) {
    return (
        <div className={cn("w-full", className)}>
            <div className="flex rounded-xl border border-border/60 bg-card/50 p-1 shadow-sm">
                {/* Autopilot */}
                <button
                    type="button"
                    onClick={() => onChange("autopilot")}
                    className={cn(
                        "flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200",
                        mode === "autopilot"
                            ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    )}
                >
                    <span className="text-lg">🤖</span>
                    <span>Autopilot</span>
                </button>

                {/* Studio */}
                <button
                    type="button"
                    onClick={() => onChange("studio")}
                    className={cn(
                        "flex-1 flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200",
                        mode === "studio"
                            ? "bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-md shadow-violet-500/20"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    )}
                >
                    <span className="text-lg">🧑‍🎨</span>
                    <span>Studio</span>
                </button>
            </div>

            {/* Description text */}
            <p className="mt-2 text-center text-xs text-muted-foreground">
                {mode === "autopilot"
                    ? "Describe what you want — AI plans and builds it automatically"
                    : "Build step-by-step — pick your tools, control each stage"}
            </p>
        </div>
    )
}
