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
// Component — matches the Gemini-generated mockup
// ---------------------------------------------------------------------------

export function ModeSelector({ mode, onChange, className }: ModeSelectorProps) {
    return (
        <div className={cn("w-full flex flex-col items-center", className)}>
            <div
                className="inline-flex rounded-full p-1.5"
                style={{
                    backgroundColor: "hsl(0 0% 94%)",
                    border: "1px solid hsl(0 0% 88%)",
                    boxShadow:
                        "inset 0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)",
                }}
            >
                {/* Autopilot */}
                <button
                    type="button"
                    onClick={() => onChange("autopilot")}
                    className="flex items-center gap-2.5 rounded-full px-7 py-3 text-sm font-semibold transition-all duration-250"
                    style={
                        mode === "autopilot"
                            ? {
                                backgroundColor: "hsl(var(--forge-accent))",
                                color: "white",
                                boxShadow:
                                    "0 2px 8px hsl(168 75% 32% / 0.35), 0 1px 2px hsl(168 75% 32% / 0.2)",
                            }
                            : {
                                backgroundColor: "transparent",
                                color: "hsl(var(--forge-text-muted))",
                            }
                    }
                >
                    <span>Autopilot</span>
                    <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.75"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >
                        <path d="M12 8V4H8" />
                        <rect width="16" height="12" x="4" y="8" rx="2" />
                        <path d="M2 14h2" />
                        <path d="M20 14h2" />
                        <path d="M15 13v2" />
                        <path d="M9 13v2" />
                    </svg>
                </button>

                {/* Studio */}
                <button
                    type="button"
                    onClick={() => onChange("studio")}
                    className="flex items-center gap-2.5 rounded-full px-7 py-3 text-sm font-semibold transition-all duration-250"
                    style={
                        mode === "studio"
                            ? {
                                backgroundColor: "hsl(var(--forge-accent))",
                                color: "white",
                                boxShadow:
                                    "0 2px 8px hsl(168 75% 32% / 0.35), 0 1px 2px hsl(168 75% 32% / 0.2)",
                            }
                            : {
                                backgroundColor: "transparent",
                                color: "hsl(var(--forge-text-muted))",
                            }
                    }
                >
                    <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.75"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >
                        <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" />
                        <path d="M12 12l8-4.5" />
                        <path d="M12 12v9" />
                        <path d="M12 12L4 7.5" />
                    </svg>
                    <span>Studio</span>
                </button>
            </div>

            {/* Description text */}
            <p
                className="mt-2.5 text-center text-xs tracking-wide"
                style={{ color: "hsl(var(--forge-text-subtle))" }}
            >
                {mode === "autopilot"
                    ? "Describe what you want — AI plans and builds it automatically"
                    : "Build step-by-step — pick your tools, control each stage"}
            </p>
        </div>
    )
}
