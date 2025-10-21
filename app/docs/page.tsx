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
                  Before installing the desktop app or running the MCP bridge
                </CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <ol className="space-y-3">
                  <li>
                    <p className="font-semibold">Install Blender 3.0+</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-1">
                      <p><strong className="text-foreground">Linux:</strong> Download from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a> or use your distribution&apos;s package manager.</p>
                      <p><strong className="text-foreground">macOS:</strong> Use the universal dmg from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a>.</p>
                      <p><strong className="text-foreground">Windows:</strong> Download the installer from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a> and follow the wizard.</p>
                    </div>
                  </li>
                  <li>
                    <p className="font-semibold">Install Python 3.10+</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-1">
                      <p><strong className="text-foreground">Linux:</strong> <code>sudo apt install python3.10</code> / <code>sudo dnf install python3.10</code></p>
                      <p><strong className="text-foreground">macOS:</strong> <code>brew install python@3.10</code> or download from <a href="https://www.python.org/downloads/" target="_blank" rel="noreferrer">python.org</a></p>
                      <p><strong className="text-foreground">Windows:</strong> Installer from <a href="https://www.python.org/downloads/windows/" target="_blank" rel="noreferrer">python.org</a> (enable “Add to PATH”)</p>
                    </div>
                  </li>
                  <li>
                    <p className="font-semibold">Install Git</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-1">
                      <p><strong className="text-foreground">Linux:</strong> <code>sudo apt install git</code> / <code>sudo dnf install git</code></p>
                      <p><strong className="text-foreground">macOS:</strong> <code>brew install git</code> or install Xcode command line tools</p>
                      <p><strong className="text-foreground">Windows:</strong> Download from <a href="https://git-scm.com/downloads" target="_blank" rel="noreferrer">git-scm.com</a></p>
                    </div>
                  </li>
                  <li>
                    <p className="font-semibold">Install the <code>uv</code> package manager</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-1">
                      <p><strong className="text-foreground">Linux:</strong> <code>curl -LsSf https://astral.sh/uv/install.sh | sh</code></p>
                      <p><strong className="text-foreground">macOS:</strong> <code>brew install uv</code> (or use the Linux script)</p>
                      <p><strong className="text-foreground">Windows (PowerShell):</strong> <code>powershell -c &quot;irm https://astral.sh/uv/install.ps1 | iex&quot;</code></p>
                      <p className="pt-1">Add the printed directory (e.g. <code>~/.local/bin</code> or <code>%USERPROFILE%\.local\bin</code>) to your PATH and verify with <code>uv --version</code>.</p>
                    </div>
                  </li>
                  <li>
                    <p className="font-semibold">Download the Blender MCP addon</p>
                    <div className="rounded-md bg-muted/40 p-3 text-sm text-muted-foreground space-y-2">
                      <a
                        href="/downloads/blender-mcp-addon.py"
                        download
                        className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90"
                      >
                        <span>Direct download</span>
                      </a>
                      <p>
                        or clone the upstream repository:
                        <br />
                        <code>git clone https://github.com/ahujasid/blender-mcp.git</code>
                      </p>
                    </div>
                  </li>
                  <li>Install the addon (Blender → Preferences → Add-ons → Install) and start the bridge with <code>uvx blender-mcp</code>.</li>
                  <li>Launch ModelForge and confirm the MCP Connection card shows “Connected”.</li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Blender MCP Setup</CardTitle>
                <CardDescription>Connect Blender to ModelForge</CardDescription>
              </CardHeader>
              <CardContent className="prose prose-slate dark:prose-invert max-w-none">
                <ol>
                  <li>
                    Install <strong>Blender 3.0+</strong>, <strong>Python 3.10+</strong>, and the{" "}
                    <code>uv</code> package manager (see <code>blendermcpreadme.md</code> or the upstream repo).
                  </li>
                  <li>
                    Download the latest <code>addon.py</code> (use our <a href="/downloads/blender-mcp-addon.py" download>direct download</a> or clone the upstream repo with <code>git clone https://github.com/ahujasid/blender-mcp.git</code>) and install it via Blender → Preferences → Add-ons → Install.
                  </li>
                  <li>
                    Start the MCP server in a terminal:
                    <pre>
{`uvx blender-mcp`}
                    </pre>
                    Match the host/port with your <code>.env</code> values (
                    <code>BLENDER_MCP_HOST</code> / <code>BLENDER_MCP_PORT</code>).
                  </li>
                  <li>
                    Open ModelForge’s dashboard. The new{" "}
                    <em>“MCP Connection”</em> card shows connectivity and lets you send a test command. The same
                    status is available in the Electron desktop app.
                  </li>
                  <li>
                    Once connected, the AI chat endpoint can translate actions into MCP commands and stream results
                    back to the UI.
                  </li>
                </ol>
                <p className="text-sm text-muted-foreground">
                  Tip: only run a single MCP instance at a time (Cursor, Claude, or ModelForge) to avoid port conflicts.
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
                  The first ModelForge AI endpoint is available for early testing. It currently
                  returns a placeholder response so you can integrate against the contract while
                  we finish the Gemini hookup.
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
