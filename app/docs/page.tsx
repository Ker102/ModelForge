import { Navbar } from "@/components/landing/navbar"
import { Footer } from "@/components/landing/footer"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function DocsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 container py-12">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-4">Documentation</h1>
            <p className="text-xl text-muted-foreground">
              Learn how to use ModelForge to supercharge your Blender workflow
            </p>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Getting Started</CardTitle>
                <CardDescription>Quick start guide for ModelForge</CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <h3>Installation</h3>
                <ol>
                  <li>Download the ModelForge desktop app from the downloads page</li>
                  <li>Install the Blender MCP server plugin</li>
                  <li>Create an account and sign in</li>
                  <li>Connect your Blender instance to ModelForge</li>
                </ol>

                <h3>Your First Project</h3>
                <ol>
                  <li>Create a new project from the dashboard</li>
                  <li>Open Blender and start the MCP server</li>
                  <li>Launch the ModelForge desktop app</li>
                  <li>Start chatting with the AI to create your 3D models</li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Features</CardTitle>
                <CardDescription>What you can do with ModelForge</CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <h3>Natural Language Commands</h3>
                <p>
                  Use everyday language to control Blender. Create objects, modify materials,
                  adjust lighting, and more through simple text commands.
                </p>

                <h3>Project Memory</h3>
                <p>
                  ModelForge remembers your project context across sessions, making it easy
                  to pick up where you left off.
                </p>

                <h3>Viewport Awareness</h3>
                <p>
                  The AI can see your Blender viewport and provide contextual suggestions
                  based on your current scene.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>API Reference</CardTitle>
                <CardDescription>For developers building integrations</CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <p>
                  The first ModelForge AI endpoint is available for early testing. It currently
                  returns a placeholder response so you can integrate against the contract while
                  we finish the Gemini hookup.
                </p>
                <h4>POST /api/ai/chat</h4>
                <pre>
{`{
  "projectId": "optional project UUID",
  "message": "Describe the lighting setup for my scene."
}`}
                </pre>
                <p>
                  The route validates project ownership, checks your plan&apos;s daily and monthly
                  AI allocation, and logs usage for billing. Free tier users will receive a limit
                  error after five requests per day. Responses include the latest usage totals:
                </p>
                <pre>
{`{
  "message": {
    "role": "assistant",
    "content": "Placeholder response until Gemini integration ships."
  },
  "usage": {
    "daily": { "used": 3, "limit": 5 },
    "monthly": { "used": 7, "limit": null }
  }
}`}
                </pre>
                <p>
                  Once LLM connectivity is live the response will contain real tool outputs and
                  conversation IDs, so you can start building your front-end today.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
