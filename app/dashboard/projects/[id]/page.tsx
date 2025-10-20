import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { notFound } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatDateTime } from "@/lib/utils"
import type { Conversation, Message } from "@prisma/client"

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
        take: 5,
        orderBy: {
          lastMessageAt: "desc",
        },
        include: {
          messages: {
            take: 1,
            orderBy: {
              createdAt: "desc",
            },
          },
        },
      },
    },
  })

  if (!project) {
    notFound()
  }

  return (
    <div className="container py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold">{project.name}</h1>
          {project.description && (
            <p className="text-muted-foreground mt-2">{project.description}</p>
          )}
          <div className="flex gap-2 mt-4">
            {project.blenderVersion && (
              <Badge variant="secondary">Blender {project.blenderVersion}</Badge>
            )}
            <Badge variant="outline">Created {formatDateTime(project.createdAt)}</Badge>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Desktop App Required</CardTitle>
            <CardDescription>
              To interact with this project, you&apos;ll need to download and connect the ModelForge desktop app
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border p-6 bg-muted/50">
              <h3 className="font-semibold mb-2">How to get started:</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
                <li>Download the ModelForge desktop app</li>
                <li>Install and run the Blender MCP server</li>
                <li>Open this project in the desktop app</li>
                <li>Start creating with AI</li>
              </ol>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Conversations</CardTitle>
            <CardDescription>
              Your AI conversation history will appear here
            </CardDescription>
          </CardHeader>
          <CardContent>
            {project.conversations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No conversations yet. Connect the desktop app to get started.
              </div>
            ) : (
              <div className="space-y-4">
                {project.conversations.map((conversation: Conversation & { messages: Message[] }) => (
                  <div key={conversation.id} className="border-l-2 border-primary pl-4">
                    <p className="text-sm text-muted-foreground">
                      {formatDateTime(conversation.lastMessageAt)}
                    </p>
                    {conversation.messages[0] && (
                      <p className="text-sm mt-1 line-clamp-2">
                        {conversation.messages[0].content}
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

