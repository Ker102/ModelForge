"use client"

import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Activity, ChevronDown, ChevronUp, Filter, Clock, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

// ============================================================================
// Types (matching server-side LogEntry / SessionSummary)
// ============================================================================

interface LogEntry {
    timestamp: string
    sessionId: string
    namespace: string
    level: "debug" | "info" | "warn" | "error"
    message: string
    data?: Record<string, unknown>
    durationMs?: number
}

interface SessionSummary {
    sessionId: string
    startedAt: string
    endedAt: string
    totalDurationMs: number
    timers: Record<string, number>
    counts: { debug: number; info: number; warn: number; error: number }
    neuralCosts: Array<{ provider: string; model: string; durationMs: number; estimatedCostUsd: number }>
    ragStats: { totalRetrieved: number; totalRelevant: number; fallbacksUsed: number }
}

// ============================================================================
// Props
// ============================================================================

interface MonitoringPanelProps {
    logs: LogEntry[]
    summary: SessionSummary | null
}

// ============================================================================
// Constants
// ============================================================================

const LEVEL_STYLES: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
    debug: { bg: "bg-zinc-800/50", text: "text-zinc-400", icon: null },
    info: { bg: "bg-teal-900/30", text: "text-teal-400", icon: <CheckCircle className="w-3 h-3" /> },
    warn: { bg: "bg-yellow-900/30", text: "text-yellow-400", icon: <AlertTriangle className="w-3 h-3" /> },
    error: { bg: "bg-red-900/30", text: "text-red-400", icon: <XCircle className="w-3 h-3" /> },
}

const NAMESPACE_COLORS: Record<string, string> = {
    planner: "text-blue-400",
    executor: "text-emerald-400",
    crag: "text-purple-400",
    neural: "text-pink-400",
    vision: "text-amber-400",
    rag: "text-indigo-400",
    strategy: "text-cyan-400",
    mcp: "text-orange-400",
    workflow: "text-lime-400",
    system: "text-zinc-500",
}

// ============================================================================
// Component
// ============================================================================

export function MonitoringPanel({ logs, summary }: MonitoringPanelProps) {
    const [isExpanded, setIsExpanded] = useState(false)
    const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set())
    const [showDebug, setShowDebug] = useState(false)

    const errorCount = logs.filter((l) => l.level === "error").length
    const warnCount = logs.filter((l) => l.level === "warn").length

    // Get unique namespaces from logs
    const namespaces = useMemo(() => {
        const ns = new Set(logs.map((l) => l.namespace))
        return Array.from(ns)
    }, [logs])

    // Filter logs
    const filteredLogs = useMemo(() => {
        return logs.filter((log) => {
            if (!showDebug && log.level === "debug") return false
            if (activeFilters.size > 0 && !activeFilters.has(log.namespace)) return false
            return true
        })
    }, [logs, showDebug, activeFilters])

    const toggleFilter = (ns: string) => {
        setActiveFilters((prev) => {
            const next = new Set(prev)
            if (next.has(ns)) {
                next.delete(ns)
            } else {
                next.add(ns)
            }
            return next
        })
    }

    const formatTime = (timestamp: string) => {
        return timestamp.split("T")[1]?.slice(0, 12) ?? ""
    }

    const formatDuration = (ms: number) => {
        if (ms < 1000) return `${ms}ms`
        return `${(ms / 1000).toFixed(1)}s`
    }

    if (logs.length === 0) return null

    return (
        <div className="border border-zinc-800 rounded-lg overflow-hidden bg-zinc-950/80 backdrop-blur-sm mt-3">
            {/* Header */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between px-3 py-2 hover:bg-zinc-900/50 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-teal-400" />
                    <span className="text-xs font-medium text-zinc-300">Pipeline Monitor</span>
                    <span className="text-xs bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded-full">
                        {logs.length}
                    </span>
                    {errorCount > 0 && (
                        <span className="text-xs bg-red-900/50 text-red-400 px-1.5 py-0.5 rounded-full">
                            {errorCount} error{errorCount !== 1 ? "s" : ""}
                        </span>
                    )}
                    {warnCount > 0 && (
                        <span className="text-xs bg-yellow-900/50 text-yellow-400 px-1.5 py-0.5 rounded-full">
                            {warnCount} warn{warnCount !== 1 ? "s" : ""}
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {summary && (
                        <span className="text-xs text-zinc-500">
                            {formatDuration(summary.totalDurationMs)}
                        </span>
                    )}
                    {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-zinc-500" />
                    ) : (
                        <ChevronDown className="w-4 h-4 text-zinc-500" />
                    )}
                </div>
            </button>

            {/* Expanded content */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        {/* Filters */}
                        <div className="flex items-center gap-1.5 px-3 py-2 border-t border-zinc-800 flex-wrap">
                            <Filter className="w-3 h-3 text-zinc-500" />
                            {namespaces.map((ns) => (
                                <button
                                    key={ns}
                                    onClick={() => toggleFilter(ns)}
                                    className={`text-[10px] px-2 py-0.5 rounded-full border transition-colors ${activeFilters.size === 0 || activeFilters.has(ns)
                                            ? `border-zinc-700 ${NAMESPACE_COLORS[ns] ?? "text-zinc-400"}`
                                            : "border-zinc-800 text-zinc-600"
                                        }`}
                                >
                                    {ns}
                                </button>
                            ))}
                            <button
                                onClick={() => setShowDebug(!showDebug)}
                                className={`text-[10px] px-2 py-0.5 rounded-full border transition-colors ml-1 ${showDebug ? "border-zinc-600 text-zinc-400" : "border-zinc-800 text-zinc-600"
                                    }`}
                            >
                                debug
                            </button>
                        </div>

                        {/* Summary card (if available) */}
                        {summary && (
                            <div className="px-3 py-2 border-t border-zinc-800 grid grid-cols-2 sm:grid-cols-4 gap-2">
                                <div className="text-center">
                                    <div className="text-xs font-mono text-teal-400">{formatDuration(summary.totalDurationMs)}</div>
                                    <div className="text-[10px] text-zinc-500">Total</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-xs font-mono text-zinc-300">{Object.keys(summary.timers).length}</div>
                                    <div className="text-[10px] text-zinc-500">Stages</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-xs font-mono text-zinc-300">{summary.ragStats.totalRelevant}/{summary.ragStats.totalRetrieved}</div>
                                    <div className="text-[10px] text-zinc-500">RAG Docs</div>
                                </div>
                                <div className="text-center">
                                    <div className={`text-xs font-mono ${summary.counts.error > 0 ? "text-red-400" : "text-emerald-400"}`}>
                                        {summary.counts.error}
                                    </div>
                                    <div className="text-[10px] text-zinc-500">Errors</div>
                                </div>
                            </div>
                        )}

                        {/* Timing bars */}
                        {summary && Object.keys(summary.timers).length > 0 && (
                            <div className="px-3 py-2 border-t border-zinc-800 space-y-1">
                                {Object.entries(summary.timers)
                                    .sort(([, a], [, b]) => b - a)
                                    .slice(0, 8)
                                    .map(([label, ms]) => {
                                        const maxMs = Math.max(...Object.values(summary.timers))
                                        const pct = maxMs > 0 ? (ms / maxMs) * 100 : 0
                                        return (
                                            <div key={label} className="flex items-center gap-2">
                                                <span className="text-[10px] text-zinc-500 w-28 truncate">{label.replace(/_/g, " ")}</span>
                                                <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-teal-600 rounded-full transition-all"
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                                <span className="text-[10px] font-mono text-zinc-400 w-14 text-right">
                                                    {formatDuration(ms)}
                                                </span>
                                            </div>
                                        )
                                    })}
                            </div>
                        )}

                        {/* Log entries */}
                        <div className="max-h-64 overflow-y-auto border-t border-zinc-800">
                            {filteredLogs.map((log, i) => {
                                const style = LEVEL_STYLES[log.level] ?? LEVEL_STYLES.debug
                                const nsColor = NAMESPACE_COLORS[log.namespace] ?? "text-zinc-400"

                                return (
                                    <div
                                        key={i}
                                        className={`flex items-start gap-2 px-3 py-1 text-[11px] font-mono ${style.bg} border-b border-zinc-900/50`}
                                    >
                                        <span className="text-zinc-600 shrink-0">{formatTime(log.timestamp)}</span>
                                        <span className={`shrink-0 w-12 uppercase font-semibold ${nsColor}`}>
                                            {log.namespace.slice(0, 6)}
                                        </span>
                                        <span className={`flex items-center gap-1 ${style.text}`}>
                                            {style.icon}
                                        </span>
                                        <span className={`${style.text} break-words`}>
                                            {log.message}
                                            {log.data && Object.keys(log.data).length > 0 && (
                                                <span className="text-zinc-600 ml-1">
                                                    {JSON.stringify(log.data).slice(0, 120)}
                                                    {JSON.stringify(log.data).length > 120 ? "…" : ""}
                                                </span>
                                            )}
                                        </span>
                                    </div>
                                )
                            })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
