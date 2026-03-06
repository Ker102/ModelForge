"use client"

import { useState, useCallback } from "react"
import { cn } from "@/lib/utils"
import {
    CATEGORIES,
    getToolsForCategory,
    type StudioCategory,
    type ToolEntry,
    type ToolInput,
} from "@/lib/orchestration/tool-catalog"

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface StudioToolPickerProps {
    onAddStep: (toolId: string, category: StudioCategory, inputs: Record<string, string>) => void
    className?: string
}

// ---------------------------------------------------------------------------
// Tool Input Form
// ---------------------------------------------------------------------------

function ToolInputField({
    input,
    value,
    onChange,
}: {
    input: ToolInput
    value: string
    onChange: (key: string, val: string) => void
}) {
    switch (input.type) {
        case "text":
            return (
                <div className="space-y-1.5">
                    <label className="block text-sm font-medium text-foreground">
                        {input.label}
                        {input.required && <span className="ml-1 text-red-400">*</span>}
                    </label>
                    <textarea
                        value={value}
                        onChange={(e) => onChange(input.key, e.target.value)}
                        placeholder={input.placeholder}
                        rows={3}
                        className="w-full rounded-lg border border-border/60 bg-background/80 px-3 py-2 text-sm placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/50 resize-none"
                    />
                    {input.helpText && (
                        <p className="text-xs text-muted-foreground/70">{input.helpText}</p>
                    )}
                </div>
            )

        case "image":
            return (
                <div className="space-y-1.5">
                    <label className="block text-sm font-medium text-foreground">
                        {input.label}
                        {input.required && <span className="ml-1 text-red-400">*</span>}
                    </label>
                    <div className="flex items-center gap-3">
                        <label className="flex-1 flex items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border/60 bg-background/50 px-4 py-6 cursor-pointer hover:border-violet-500/40 hover:bg-violet-500/5 transition-colors">
                            <span className="text-2xl">📷</span>
                            <span className="text-sm text-muted-foreground">
                                {value ? "Image selected ✓" : "Click to upload"}
                            </span>
                            <input
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={(e) => {
                                    const file = e.target.files?.[0]
                                    if (file) {
                                        const reader = new FileReader()
                                        reader.onload = () =>
                                            onChange(input.key, reader.result as string)
                                        reader.readAsDataURL(file)
                                    }
                                }}
                            />
                        </label>
                    </div>
                    {input.helpText && (
                        <p className="text-xs text-muted-foreground/70">{input.helpText}</p>
                    )}
                </div>
            )

        case "select":
            return (
                <div className="space-y-1.5">
                    <label className="block text-sm font-medium text-foreground">
                        {input.label}
                    </label>
                    <div className="space-y-1.5">
                        {input.options?.map((opt) => (
                            <button
                                key={opt.value}
                                type="button"
                                onClick={() => onChange(input.key, opt.value)}
                                className={cn(
                                    "w-full flex items-center gap-3 p-3 rounded-lg border text-left text-sm transition-all",
                                    (value || input.defaultValue) === opt.value
                                        ? "border-violet-500/60 bg-violet-500/10 text-foreground"
                                        : "border-border/40 bg-background/50 text-muted-foreground hover:border-border"
                                )}
                            >
                                <div className="flex-1">
                                    <span className="font-medium">{opt.label}</span>
                                    {opt.description && (
                                        <span className="ml-2 text-xs text-muted-foreground/70">
                                            — {opt.description}
                                        </span>
                                    )}
                                </div>
                                {(value || input.defaultValue) === opt.value && (
                                    <span className="text-violet-400">✓</span>
                                )}
                            </button>
                        ))}
                    </div>
                    {input.helpText && (
                        <p className="text-xs text-muted-foreground/70">{input.helpText}</p>
                    )}
                </div>
            )

        case "slider":
            return (
                <div className="space-y-1.5">
                    <label className="block text-sm font-medium text-foreground">
                        {input.label}: {value || input.defaultValue}
                    </label>
                    <input
                        type="range"
                        min={input.min}
                        max={input.max}
                        step={input.step}
                        value={value || input.defaultValue}
                        onChange={(e) => onChange(input.key, e.target.value)}
                        className="w-full accent-violet-500"
                    />
                    {input.helpText && (
                        <p className="text-xs text-muted-foreground/70">{input.helpText}</p>
                    )}
                </div>
            )

        default:
            return null
    }
}

// ---------------------------------------------------------------------------
// Tool Card
// ---------------------------------------------------------------------------

const DIFFICULTY_BADGES: Record<string, { label: string; color: string }> = {
    beginner: { label: "Beginner friendly", color: "bg-green-500/15 text-green-400 border-green-500/30" },
    intermediate: { label: "Some experience", color: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30" },
    advanced: { label: "Advanced", color: "bg-red-500/15 text-red-400 border-red-500/30" },
}

function ToolCard({
    tool,
    isSelected,
    onSelect,
    inputValues,
    onInputChange,
    onAddStep,
}: {
    tool: ToolEntry
    isSelected: boolean
    onSelect: () => void
    inputValues: Record<string, string>
    onInputChange: (key: string, val: string) => void
    onAddStep: () => void
}) {
    const [showHelp, setShowHelp] = useState(false)
    const diff = DIFFICULTY_BADGES[tool.difficulty]
    const hasRequiredInputs = tool.inputs
        .filter((i) => i.required)
        .every((i) => inputValues[i.key]?.trim())

    return (
        <div
            className={cn(
                "rounded-xl border transition-all duration-200",
                isSelected
                    ? "border-violet-500/50 bg-violet-500/5 shadow-lg shadow-violet-500/10"
                    : "border-border/40 bg-card/50 hover:border-border/80 hover:shadow-sm"
            )}
        >
            {/* Header */}
            <button
                type="button"
                onClick={onSelect}
                className="w-full p-4 text-left"
            >
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-sm text-foreground">{tool.name}</h4>
                            {tool.type === "neural" && (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-500/15 text-blue-400 border border-blue-500/30">
                                    AI Model
                                </span>
                            )}
                        </div>
                        <p className="text-sm text-muted-foreground">{tool.tagline}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1.5 shrink-0">
                        <span className={cn("px-2 py-0.5 rounded-full text-[10px] font-medium border", diff.color)}>
                            {diff.label}
                        </span>
                        {tool.cost && (
                            <span className="text-[10px] text-muted-foreground/60">{tool.cost}</span>
                        )}
                    </div>
                </div>
                <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground/60">
                    <span>⏱ {tool.estimatedTime}</span>
                </div>
            </button>

            {/* Help section */}
            {isSelected && (
                <div className="border-t border-border/30 px-4 py-2">
                    <button
                        type="button"
                        onClick={() => setShowHelp(!showHelp)}
                        className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
                    >
                        {showHelp ? "▼ Hide details" : "▶ What is this?"}
                    </button>
                    {showHelp && (
                        <div className="mt-2 space-y-2 text-xs text-muted-foreground">
                            <p>{tool.description}</p>
                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <span className="font-medium text-green-400/80">Best for:</span>
                                    <ul className="mt-1 space-y-0.5">
                                        {tool.bestFor.map((item) => (
                                            <li key={item}>✓ {item}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="flex-1">
                                    <span className="font-medium text-red-400/80">Not ideal for:</span>
                                    <ul className="mt-1 space-y-0.5">
                                        {tool.notFor.map((item) => (
                                            <li key={item}>✗ {item}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Input form */}
            {isSelected && (
                <div className="border-t border-border/30 p-4 space-y-4">
                    {tool.inputs.map((input) => (
                        <ToolInputField
                            key={input.key}
                            input={input}
                            value={inputValues[input.key] ?? ""}
                            onChange={onInputChange}
                        />
                    ))}

                    <button
                        type="button"
                        onClick={onAddStep}
                        disabled={!hasRequiredInputs}
                        className={cn(
                            "w-full py-2.5 px-4 rounded-lg text-sm font-medium transition-all",
                            hasRequiredInputs
                                ? "bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-md shadow-violet-500/20 hover:shadow-lg hover:shadow-violet-500/30"
                                : "bg-muted/50 text-muted-foreground cursor-not-allowed"
                        )}
                    >
                        Add to Workflow →
                    </button>
                </div>
            )}
        </div>
    )
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export function StudioToolPicker({ onAddStep, className }: StudioToolPickerProps) {
    const [activeCategory, setActiveCategory] = useState<StudioCategory>("shape")
    const [selectedToolId, setSelectedToolId] = useState<string | null>(null)
    const [inputValues, setInputValues] = useState<Record<string, string>>({})

    const tools = getToolsForCategory(activeCategory)

    const handleCategoryChange = useCallback((cat: StudioCategory) => {
        setActiveCategory(cat)
        setSelectedToolId(null)
        setInputValues({})
    }, [])

    const handleInputChange = useCallback((key: string, val: string) => {
        setInputValues((prev) => ({ ...prev, [key]: val }))
    }, [])

    const handleAddStep = useCallback(() => {
        if (!selectedToolId) return
        onAddStep(selectedToolId, activeCategory, inputValues)
        setSelectedToolId(null)
        setInputValues({})
    }, [selectedToolId, activeCategory, inputValues, onAddStep])

    return (
        <div className={cn("flex flex-col h-full", className)}>
            {/* Category tabs */}
            <div className="flex gap-1 overflow-x-auto pb-2 px-1 scrollbar-thin">
                {CATEGORIES.map((cat) => (
                    <button
                        key={cat.id}
                        type="button"
                        onClick={() => handleCategoryChange(cat.id)}
                        className={cn(
                            "shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap",
                            activeCategory === cat.id
                                ? "bg-violet-500/15 text-violet-300 border border-violet-500/40"
                                : "text-muted-foreground hover:text-foreground hover:bg-muted/30 border border-transparent"
                        )}
                    >
                        <span>{cat.icon}</span>
                        <span>{cat.label}</span>
                    </button>
                ))}
            </div>

            {/* Category description */}
            <div className="px-1 py-2">
                <p className="text-xs text-muted-foreground/70">
                    {CATEGORIES.find((c) => c.id === activeCategory)?.helpText}
                </p>
            </div>

            {/* Tool cards */}
            <div className="flex-1 overflow-y-auto space-y-2 px-1">
                {tools.map((tool) => (
                    <ToolCard
                        key={tool.id}
                        tool={tool}
                        isSelected={selectedToolId === tool.id}
                        onSelect={() =>
                            setSelectedToolId(selectedToolId === tool.id ? null : tool.id)
                        }
                        inputValues={inputValues}
                        onInputChange={handleInputChange}
                        onAddStep={handleAddStep}
                    />
                ))}
            </div>
        </div>
    )
}
