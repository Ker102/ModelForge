/**
 * Studio Advisor API — Lightweight advisory endpoint.
 *
 * Answers questions about tools, concepts, and workflow.
 * NEVER executes actions — purely informational.
 */

import { NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"
import { GoogleGenerativeAI } from "@google/generative-ai"
import { CATEGORIES, TOOLS } from "@/lib/orchestration/tool-catalog"

// ---------------------------------------------------------------------------
// System prompt
// ---------------------------------------------------------------------------

const ADVISOR_SYSTEM_PROMPT = `You are the ModelForge Studio Assistant — a friendly, knowledgeable guide for 3D creation.

Your role:
- Help users choose the right tools for their project
- Explain 3D concepts in simple, beginner-friendly terms
- Suggest next steps based on their current workflow
- Troubleshoot errors and recommend solutions
- Never execute actions — you only advise

You know about these pipeline categories:
${CATEGORIES.map((c) => `- ${c.icon} ${c.label}: ${c.description} — ${c.helpText}`).join("\n")}

You know about these tools:
${Object.values(TOOLS).map((t) => `- ${t.name} (${t.category}): ${t.tagline}. Best for: ${t.bestFor.join(", ")}. Not ideal for: ${t.notFor.join(", ")}`).join("\n")}

Rules:
1. Keep answers concise (2-4 sentences for simple questions)
2. Use emoji and friendly tone
3. When recommending tools, explain WHY in simple terms
4. If asked about something outside ModelForge, politely redirect
5. For error troubleshooting, ask for specific error messages
6. Always suggest the beginner-friendly option first
7. Mention costs/time estimates when relevant`

// ---------------------------------------------------------------------------
// Route handler
// ---------------------------------------------------------------------------

export async function POST(request: Request) {
    try {
        // Auth check
        const supabase = await createClient()
        const {
            data: { user },
        } = await supabase.auth.getUser()

        if (!user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
        }

        const body = await request.json()
        const { message, workflowContext } = body

        if (!message || typeof message !== "string") {
            return NextResponse.json({ error: "Message is required" }, { status: 400 })
        }

        // Build context-aware prompt
        let contextNote = ""
        if (workflowContext) {
            if (workflowContext.currentStep) {
                contextNote += `\nThe user is currently on step: ${workflowContext.currentStep}`
            }
            if (workflowContext.completedSteps?.length) {
                contextNote += `\nCompleted steps: ${workflowContext.completedSteps.join(", ")}`
            }
            if (workflowContext.lastError) {
                contextNote += `\nLast error encountered: ${workflowContext.lastError}`
            }
        }

        const apiKey = process.env.GEMINI_API_KEY
        if (!apiKey) {
            return NextResponse.json(
                { response: "The AI assistant is not configured. Please set up your Gemini API key." },
                { status: 200 }
            )
        }

        const genAI = new GoogleGenerativeAI(apiKey)
        const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" })

        const result = await model.generateContent({
            contents: [
                {
                    role: "user",
                    parts: [
                        {
                            text: `${ADVISOR_SYSTEM_PROMPT}${contextNote}\n\nUser question: ${message}`,
                        },
                    ],
                },
            ],
            generationConfig: {
                maxOutputTokens: 500,
                temperature: 0.7,
            },
        })

        const response = result.response.text()

        return NextResponse.json({ response })
    } catch (error) {
        console.error("[Advisor API Error]", error)
        return NextResponse.json(
            { response: "Sorry, I had trouble processing that. Please try again." },
            { status: 200 }
        )
    }
}
