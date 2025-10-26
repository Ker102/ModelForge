import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { notFound } from "next/navigation"
import { formatDateTime } from "@/lib/utils"
import { ProjectChat } from "@/components/projects/project-chat"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Conversation, Message } from "@prisma/client"
import { getUsageSummary } from "@/lib/usage"
import { SubscriptionTier } from "@/lib/subscription"
import { parsePlanningMetadata } from "@/lib/orchestration/plan-utils"
import type { PlanningMetadata } from "@/lib/orchestration/types"

type CommandStub = {
  id: string
  tool: string
  description: string
  status: string
  confidence?: number
  arguments?: Record<string, unknown>
  notes?: string
}

const extractPlanFromMessage = (message: Message): PlanningMetadata | undefined => {
  const results = message.mcpResults as Record<string, unknown> | null
  if (!results || typeof results !== "object") return undefined
  const rawPlan = (results as Record<string, unknown>).plan
  return parsePlanningMetadata(rawPlan)
}

const mapMessageToChat = (message: Message) => ({
  id: message.id,
  role: message.role === "assistant" ? "assistant" : "user",
  content: message.content,
  createdAt: message.createdAt.toISOString(),
  mcpCommands: Array.isArray(message.mcpCommands)
    ? (message.mcpCommands as CommandStub[])
    : undefined,
  plan: extractPlanFromMessage(message),
})

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const session = await auth()
  
  if (!session?.user) {
    return null
  }

  const project = await prisma.project.findFirst({
    where: {
      id: params.id,
      userId: session.user.id,
      isDeleted: false,
    },
    include: {
      conversations: {
        orderBy: {
          lastMessageAt: "desc",
        },
        include: {
          messages: {
            orderBy: {
              createdAt: "desc",
            },
            take: 20,
          },
        },
      },
    },
  })

  if (!project) {
    notFound()
  }

  const tier: SubscriptionTier =
    session.user.subscriptionTier === "starter" || session.user.subscriptionTier === "pro"
      ? (session.user.subscriptionTier as SubscriptionTier)
      : "free"

  const usage = await getUsageSummary(session.user.id, tier)

  const [activeConversation, ...previousConversations] = project.conversations

  const initialConversation = activeConversation
    ? {
        id: activeConversation.id,
        messages: activeConversation.messages
          .slice()
          .sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime())
          .slice(-20)
          .map(mapMessageToChat),
      }
    : null

  const conversationHistory = previousConversations
    .map((conversation) => {
      if (!conversation) return null

      return {
        id: conversation.id,
        lastMessageAt: conversation.lastMessageAt.toISOString(),
        preview: conversation.messages[0]?.content ?? undefined,
        messages: conversation.messages
          .slice()
          .sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime())
          .slice(-20)
          .map(mapMessageToChat),
      }
    })
    .filter((conversation): conversation is NonNullable<typeof conversation> => Boolean(conversation))
    .sort((a, b) => new Date(b.lastMessageAt).getTime() - new Date(a.lastMessageAt).getTime())

  return (
    <div className="container py-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold">{project.name}</h1>
          {project.description && (
            <p className="text-muted-foreground mt-2">{project.description}</p>
          )}
          <div className="flex flex-wrap gap-2 mt-4">
            {project.blenderVersion && (
              <Badge variant="secondary">Blender {project.blenderVersion}</Badge>
            )}
            <Badge variant="outline">Created {formatDateTime(project.createdAt)}</Badge>
          </div>
        </div>

        <ProjectChat
          projectId={project.id}
          initialConversation={initialConversation}
          initialUsage={usage}
          conversationHistory={conversationHistory}
          initialAssetConfig={{
            allowHyper3d: Boolean(project.allowHyper3dAssets),
            allowSketchfab: Boolean(project.allowSketchfabAssets),
            allowPolyHaven: project.allowPolyHavenAssets !== false,
          }}
        />

        <Card>
          <CardHeader>
            <CardTitle>Connect to Blender</CardTitle>
            <CardDescription>
              Use the desktop add-on for viewport awareness and direct MCP command execution.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border p-4 space-y-2">
                <h3 className="font-semibold">Web experience</h3>
                <p className="text-sm text-muted-foreground">
                  Chat with ModelForge directly in the browser. Great for planning scenes,
                  drafting scripts, or reviewing AI suggestions on the go.
                </p>
              </div>
              <div className="rounded-lg border p-4 space-y-2 bg-muted/40">
                <h3 className="font-semibold">Blender integration (recommended)</h3>
                <p className="text-sm text-muted-foreground">
                  Install the ModelForge desktop app and Blender MCP extension for real-time viewport
                  snapshots and one-click command execution inside Blender.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Conversation History</CardTitle>
            <CardDescription>
              Once you close a session, it appears here so you can revisit or continue later.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {project.conversations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No conversations yet. Start chatting with ModelForge to build your history.
              </div>
            ) : (
              <div className="space-y-4">
                {(previousConversations.length > 0 ? previousConversations : [activeConversation])
                  .filter(Boolean)
                  .map((conversation) => (
                    <div
                      key={(conversation as Conversation).id}
                      className="border-l-2 border-primary pl-4"
                    >
                      <p className="text-sm text-muted-foreground">
                        {formatDateTime((conversation as Conversation).lastMessageAt)}
                      </p>
                      {(conversation as Conversation & { messages: Message[] }).messages[0] && (
                        <p className="text-sm mt-1 line-clamp-2">
                          {(conversation as Conversation & { messages: Message[] }).messages[0].content}
                        </p>
                      )}
                    </div>
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
