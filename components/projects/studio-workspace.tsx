"use client"

import { useState } from "react"
import {
    CATEGORIES,
    getToolsForCategory,
    type CategoryMeta,
    type StudioCategory,
    type ToolEntry,
    type ToolInput,
} from "@/lib/orchestration/tool-catalog"

interface StudioWorkspaceProps {
    activeCategory: string
    onToolSelect: (tool: ToolEntry, inputs: Record<string, string>) => void
}

function DifficultyBadge({ level }: { level: string }) {
    const colors: Record<string, { bg: string; text: string }> = {
        beginner: { bg: "hsl(var(--forge-accent-subtle))", text: "hsl(var(--forge-accent))" },
        intermediate: { bg: "hsl(48 96% 95%)", text: "hsl(40 80% 40%)" },
        advanced: { bg: "hsl(0 80% 95%)", text: "hsl(0 60% 45%)" },
    }
    const c = colors[level] ?? colors.beginner
    return (
        <span
            className="px-2 py-0.5 rounded-full text-xs font-medium capitalize"
            style={{ backgroundColor: c.bg, color: c.text }}
        >
            {level === "beginner" ? "Beginner friendly" : level}
        </span>
    )
}

function ToolTypeBadge({ type }: { type: string }) {
    if (type === "neural") {
        return (
            <span
                className="px-2 py-0.5 rounded-full text-xs font-semibold"
                style={{
                    backgroundColor: "hsl(var(--forge-accent-muted))",
                    color: "hsl(var(--forge-accent))",
                }}
            >
                AI Model
            </span>
        )
    }
    return null
}

function ToolCard({
    tool,
    onSelect,
}: {
    tool: ToolEntry
    onSelect: (tool: ToolEntry, inputs: Record<string, string>) => void
}) {
    const [expanded, setExpanded] = useState(false)
    const [inputs, setInputs] = useState<Record<string, string>>({})
    const [showHelp, setShowHelp] = useState(false)

    const handleSubmit = () => {
        onSelect(tool, inputs)
        setInputs({})
        setExpanded(false)
    }

    return (
        <div
            className="rounded-2xl border transition-all duration-200 hover:shadow-md overflow-hidden"
            style={{
                backgroundColor: "var(--forge-glass)",
                borderColor: "hsl(var(--forge-border))",
                backdropFilter: "blur(12px)",
                boxShadow: expanded ? "var(--forge-shadow-lg)" : "var(--forge-shadow)",
            }}
        >
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full text-left p-5"
            >
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                            <h3
                                className="font-semibold text-base"
                                style={{ color: "hsl(var(--forge-text))" }}
                            >
                                {tool.name}
                            </h3>
                            <ToolTypeBadge type={tool.type} />
                            <DifficultyBadge level={tool.difficulty} />
                        </div>
                        <p
                            className="text-sm mt-1.5 line-clamp-2"
                            style={{ color: "hsl(var(--forge-text-muted))" }}
                        >
                            {tool.tagline}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4 mt-3">
                    {tool.cost && (
                        <span
                            className="text-xs font-medium"
                            style={{ color: "hsl(var(--forge-text-subtle))" }}
                        >
                            {tool.cost}
                        </span>
                    )}
                    {tool.estimatedTime && (
                        <span
                            className="text-xs flex items-center gap-1"
                            style={{ color: "hsl(var(--forge-text-subtle))" }}
                        >
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10" />
                                <polyline points="12 6 12 12 16 14" />
                            </svg>
                            {tool.estimatedTime}
                        </span>
                    )}
                </div>
            </button>

            {expanded && (
                <div className="px-5 pb-5">
                    {/* Description */}
                    <p
                        className="text-xs leading-relaxed mb-3"
                        style={{ color: "hsl(var(--forge-text-muted))" }}
                    >
                        {tool.description}
                    </p>

                    {/* Best for / Not for */}
                    <div className="flex flex-wrap gap-1.5 mb-3">
                        {tool.bestFor.slice(0, 3).map((tag) => (
                            <span
                                key={tag}
                                className="px-2 py-0.5 rounded-full text-[10px] font-medium"
                                style={{
                                    backgroundColor: "hsl(var(--forge-accent-subtle))",
                                    color: "hsl(var(--forge-accent))",
                                }}
                            >
                                ✓ {tag}
                            </span>
                        ))}
                    </div>

                    {/* Help button */}
                    {(tool.inputs?.[0]?.helpText || tool.notFor?.length > 0) && (
                        <button
                            onClick={() => setShowHelp(!showHelp)}
                            className="text-xs font-medium flex items-center gap-1 mb-3"
                            style={{ color: "hsl(var(--forge-accent))" }}
                        >
                            {showHelp ? "▾" : "▸"} {showHelp ? "Hide tips" : "Show tips"}
                        </button>
                    )}
                    {showHelp && (
                        <div
                            className="text-xs leading-relaxed mb-3 p-3 rounded-xl space-y-1"
                            style={{
                                backgroundColor: "hsl(var(--forge-accent-subtle))",
                                color: "hsl(var(--forge-text-muted))",
                            }}
                        >
                            {tool.notFor.length > 0 && (
                                <p><strong>Not ideal for:</strong> {tool.notFor.join(", ")}</p>
                            )}
                        </div>
                    )}

                    {/* Input form */}
                    {tool.inputs && tool.inputs.length > 0 && (
                        <div className="space-y-3">
                            <div className="h-px" style={{ backgroundColor: "hsl(var(--forge-border))" }} />
                            {tool.inputs.map((input: ToolInput) => (
                                <div key={input.key}>
                                    <label
                                        className="block text-xs font-medium mb-1.5"
                                        style={{ color: "hsl(var(--forge-text-muted))" }}
                                    >
                                        {input.label}
                                    </label>
                                    {input.type === "text" && (
                                        <textarea
                                            value={inputs[input.key] ?? ""}
                                            onChange={(e) =>
                                                setInputs({ ...inputs, [input.key]: e.target.value })
                                            }
                                            placeholder={input.placeholder}
                                            rows={3}
                                            className="w-full rounded-xl border px-3.5 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 transition"
                                            style={{
                                                borderColor: "hsl(var(--forge-border))",
                                                backgroundColor: "hsl(var(--forge-surface-dim))",
                                                color: "hsl(var(--forge-text))",
                                            }}
                                        />
                                    )}
                                    {input.type === "select" && (
                                        <select
                                            value={inputs[input.key] ?? (input.defaultValue?.toString() ?? "")}
                                            onChange={(e) =>
                                                setInputs({ ...inputs, [input.key]: e.target.value })
                                            }
                                            className="w-full rounded-xl border px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 transition"
                                            style={{
                                                borderColor: "hsl(var(--forge-border))",
                                                backgroundColor: "hsl(var(--forge-surface-dim))",
                                                color: "hsl(var(--forge-text))",
                                            }}
                                        >
                                            <option value="">Select...</option>
                                            {input.options?.map((opt) => (
                                                <option key={opt.value} value={opt.value}>
                                                    {opt.label}{opt.description ? ` — ${opt.description}` : ""}
                                                </option>
                                            ))}
                                        </select>
                                    )}
                                    {input.type === "image" && (
                                        <div
                                            className="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer hover:border-[hsl(var(--forge-accent))] transition"
                                            style={{
                                                borderColor: "hsl(var(--forge-border))",
                                                backgroundColor: "hsl(var(--forge-surface-dim))",
                                            }}
                                        >
                                            <p className="text-xs" style={{ color: "hsl(var(--forge-text-subtle))" }}>
                                                Drop image here or click to upload
                                            </p>
                                        </div>
                                    )}
                                    {input.type === "slider" && (
                                        <input
                                            type="range"
                                            min={input.min ?? 0}
                                            max={input.max ?? 100}
                                            step={input.step ?? 1}
                                            value={inputs[input.key] ?? input.defaultValue ?? "50"}
                                            onChange={(e) =>
                                                setInputs({ ...inputs, [input.key]: e.target.value })
                                            }
                                            className="w-full accent-[hsl(var(--forge-accent))]"
                                        />
                                    )}
                                    {input.helpText && (
                                        <p
                                            className="text-[10px] mt-1"
                                            style={{ color: "hsl(var(--forge-text-subtle))" }}
                                        >
                                            {input.helpText}
                                        </p>
                                    )}
                                </div>
                            ))}

                            <button
                                onClick={handleSubmit}
                                className="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-all duration-200 hover:opacity-90"
                                style={{ backgroundColor: "hsl(var(--forge-accent))" }}
                            >
                                Add to Workflow
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export function StudioWorkspace({ activeCategory, onToolSelect }: StudioWorkspaceProps) {
    const category = CATEGORIES.find((c: CategoryMeta) => c.id === activeCategory)
    const tools = getToolsForCategory(activeCategory as StudioCategory)

    if (!category) return null

    return (
        <div className="flex-1 overflow-y-auto p-6">
            <div className="mb-6">
                <h2
                    className="text-2xl font-bold"
                    style={{ color: "hsl(var(--forge-text))" }}
                >
                    {category.label}
                </h2>
                <p
                    className="text-sm mt-1"
                    style={{ color: "hsl(var(--forge-text-muted))" }}
                >
                    {category.description}
                </p>
                <p
                    className="text-xs mt-2"
                    style={{ color: "hsl(var(--forge-text-subtle))" }}
                >
                    {category.helpText}
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {tools.map((tool: ToolEntry) => (
                    <ToolCard key={tool.id} tool={tool} onSelect={onToolSelect} />
                ))}
            </div>

            {tools.length === 0 && (
                <div
                    className="flex flex-col items-center justify-center py-16 rounded-2xl border"
                    style={{
                        borderColor: "hsl(var(--forge-border))",
                        backgroundColor: "hsl(var(--forge-surface-dim))",
                    }}
                >
                    <p style={{ color: "hsl(var(--forge-text-muted))" }}>
                        No tools available for this category yet.
                    </p>
                </div>
            )}
        </div>
    )
}
