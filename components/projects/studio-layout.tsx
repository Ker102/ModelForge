"use client"

import { useState, useCallback } from "react"
import { StudioSidebar } from "./studio-sidebar"
import { StudioWorkspace } from "./studio-workspace"
import { StudioAdvisor } from "./studio-advisor"
import { WorkflowTimeline, type WorkflowTimelineStep } from "./workflow-timeline"
import type { ToolEntry } from "@/lib/orchestration/tool-catalog"

interface StudioLayoutProps {
    projectId: string
}

export function StudioLayout({ projectId }: StudioLayoutProps) {
    const [activeCategory, setActiveCategory] = useState("shape")
    const [assistantOpen, setAssistantOpen] = useState(false)
    const [workflowSteps, setWorkflowSteps] = useState<WorkflowTimelineStep[]>([])

    const handleToolSelect = useCallback(
        (tool: ToolEntry, inputs: Record<string, string>) => {
            const step: WorkflowTimelineStep = {
                id: `step-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
                title: tool.name,
                toolName: tool.id,
                status: "pending",
            }
            setWorkflowSteps((prev) => [...prev, step])
            console.log("[Studio] Tool added to workflow:", tool.id, inputs)
        },
        []
    )

    const handleRemoveStep = useCallback((stepId: string) => {
        setWorkflowSteps((prev) => prev.filter((s) => s.id !== stepId))
    }, [])

    const handleRunAll = useCallback(() => {
        console.log("[Studio] Run all workflow steps:", workflowSteps)
    }, [workflowSteps])

    const handleToolRunNow = useCallback(
        (tool: ToolEntry, inputs: Record<string, string>) => {
            const step: WorkflowTimelineStep = {
                id: `run-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
                title: tool.name,
                toolName: tool.id,
                status: "running",
            }
            setWorkflowSteps((prev) => [...prev, step])
            console.log("[Studio] Running tool immediately:", tool.id, inputs)
            // TODO: call workflow-step API directly for immediate execution
        },
        []
    )

    return (
        <div
            className="flex flex-col rounded-2xl border overflow-hidden"
            style={{
                borderColor: "hsl(var(--forge-border))",
                backgroundColor: "hsl(var(--forge-surface))",
                height: "calc(100vh - 200px)",
                minHeight: "500px",
            }}
        >
            <div className="flex flex-1 overflow-hidden">
                <StudioSidebar
                    activeCategory={activeCategory}
                    onCategoryChange={setActiveCategory}
                    onAssistantToggle={() => setAssistantOpen((o) => !o)}
                    assistantOpen={assistantOpen}
                />

                <StudioWorkspace
                    activeCategory={activeCategory}
                    onToolSelect={handleToolSelect}
                    onToolRunNow={handleToolRunNow}
                />

                <StudioAdvisor
                    open={assistantOpen}
                    onClose={() => setAssistantOpen(false)}
                    projectId={projectId}
                />
            </div>

            <WorkflowTimeline
                steps={workflowSteps}
                onRemoveStep={handleRemoveStep}
                onRunAll={handleRunAll}
            />
        </div>
    )
}
