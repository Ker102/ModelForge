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
                <CardTitle>Quick Start Checklist</CardTitle>
                <CardDescription>
                  Get connected in three steps — no extra tools required
                </CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <ol className="space-y-3">
                  <li>
                    <p className="font-semibold">Install Blender 3.0+</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-1">
                      <p>Download from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a> and follow the installer for your platform.</p>
                    </div>
                  </li>
                  <li>
                    <p className="font-semibold">Install the ModelForge addon in Blender</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-2">
                      <p>The addon is bundled with the ModelForge desktop app. You can also download it directly:</p>
                      <a
                        href="/downloads/blender-mcp-addon.py"
                        download
                        className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90"
                      >
                        <span>Download addon</span>
                      </a>
                      <p className="pt-1">In Blender, go to <strong>Edit → Preferences → Add-ons → Install</strong>, select the downloaded file, and enable <strong>&quot;Interface: ModelForge Blender&quot;</strong>.</p>
                    </div>
                  </li>
                  <li>
                    <p className="font-semibold">Connect to ModelForge</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-1">
                      <p>In Blender&apos;s 3D View, press <strong>N</strong> to open the sidebar, click the <strong>ModelForge</strong> tab, and hit <strong>&quot;Connect to ModelForge&quot;</strong>.</p>
                      <p className="pt-1">Back in the ModelForge dashboard, the <em>MCP Connection</em> card should show &quot;Connected&quot;. You&apos;re ready to go!</p>
                    </div>
                  </li>
                </ol>
                <div className="mt-4 rounded-md bg-muted/40 p-3 text-sm text-muted-foreground">
                  <p className="font-semibold text-foreground">No extra dependencies needed</p>
                  <p>ModelForge bundles everything — no separate Python, Git, or <code>uv</code> install required. The addon runs inside Blender&apos;s built-in Python and communicates directly with ModelForge over a local socket connection.</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>How It Works</CardTitle>
                <CardDescription>How ModelForge controls Blender</CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <p>
                  The ModelForge addon creates a lightweight socket server inside Blender (port 9876 by default).
                  When you send a prompt in ModelForge, the AI generates Blender Python code, which is sent
                  to the addon and executed directly in your scene.
                </p>
                <h4>Architecture</h4>
                <ol>
                  <li>You type a natural-language instruction in the ModelForge chat.</li>
                  <li>The orchestration engine plans the steps and generates Blender Python code via Gemini.</li>
                  <li>ModelForge sends the code to the addon over a local TCP socket.</li>
                  <li>The addon executes the code inside Blender and returns results.</li>
                  <li>ModelForge can also request viewport screenshots for visual feedback loops.</li>
                </ol>
                <p className="text-sm text-muted-foreground">
                  Tip: only run one connection to the addon at a time (Cursor, Claude Desktop, or ModelForge) to avoid port conflicts.
                </p>
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
                  The ModelForge AI endpoint streams responses as NDJSON chunks for real-time updates.
                </p>
                <h4>POST /api/ai/chat</h4>
                <pre>
{`{
  "projectId": "uuid-of-project",
  "conversationId": "optional-conversation-uuid",
  "startNew": true,
  "message": "Describe the lighting setup for my scene."
}`}
                </pre>
                <p>
                  The endpoint verifies project ownership, enforces daily/monthly limits, and
                  persists both sides of the conversation. Omitting <code>conversationId</code>
                  (or passing <code>startNew: true</code>) spins up a fresh session for the project.
                </p>
                <pre>
{`{
  "conversationId": "uuid",
  "messages": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ],
  "usage": {
    "daily": { "used": 3, "limit": 5 },
    "monthly": { "used": 7, "limit": null }
  },
  "tokenUsage": {
    "promptTokens": 420,
    "responseTokens": 180,
    "totalTokens": 600
  }
}`}
                </pre>
                <p>
                  Responses stream back as NDJSON chunks so you can surface deltas instantly. Expect
                  an <code>init</code> event followed by multiple <code>delta</code> payloads, and
                  a final <code>complete</code> block like the one above. On limit exhaustion the
                  API responds with <code>429</code> and the current usage so you can prompt the
                  user to upgrade or wait for resets.
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
