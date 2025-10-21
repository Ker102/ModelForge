"use client"

import Link from "next/link"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ExternalLink, Download } from "lucide-react"

export function QuickStartCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Start</CardTitle>
        <CardDescription>Everything you need before connecting Blender</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <ol className="space-y-3 list-decimal list-inside">
          <li>
            <p className="font-semibold">Install Blender 3.0+</p>
            <div className="mt-2 space-y-1 rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
              <p><span className="font-medium text-foreground">Linux:</span> Download from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a> or use your distribution&apos;s package manager.</p>
              <p><span className="font-medium text-foreground">macOS:</span> Grab the universal dmg from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a> and drag Blender into Applications.</p>
              <p><span className="font-medium text-foreground">Windows:</span> Download the installer from <a href="https://www.blender.org/download/" target="_blank" rel="noreferrer">blender.org</a> and follow the setup wizard.</p>
            </div>
          </li>
          <li>
            <p className="font-semibold">Install Python 3.10+</p>
            <div className="mt-2 space-y-1 rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
              <p><span className="font-medium text-foreground">Linux:</span> <code>sudo apt install python3.10</code> / <code>sudo dnf install python3.10</code></p>
              <p><span className="font-medium text-foreground">macOS:</span> <code>brew install python@3.10</code> or download from <a href="https://www.python.org/downloads/" target="_blank" rel="noreferrer">python.org</a></p>
              <p><span className="font-medium text-foreground">Windows:</span> Installer from <a href="https://www.python.org/downloads/windows/" target="_blank" rel="noreferrer">python.org</a> (check “Add to PATH”)</p>
            </div>
          </li>
          <li>
            <p className="font-semibold">Install Git</p>
            <div className="mt-2 space-y-1 rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
              <p><span className="font-medium text-foreground">Linux:</span> <code>sudo apt install git</code> / <code>sudo dnf install git</code></p>
              <p><span className="font-medium text-foreground">macOS:</span> <code>brew install git</code> or install Xcode command line tools</p>
              <p><span className="font-medium text-foreground">Windows:</span> Download from <a href="https://git-scm.com/downloads" target="_blank" rel="noreferrer">git-scm.com</a></p>
            </div>
          </li>
          <li>
            <p className="font-semibold">Install the <code>uv</code> package manager</p>
            <div className="mt-2 space-y-1 rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
              <p><span className="font-medium text-foreground">Linux:</span> <code>curl -LsSf https://astral.sh/uv/install.sh | sh</code></p>
              <p><span className="font-medium text-foreground">macOS:</span> <code>brew install uv</code> (or use the Linux script)</p>
              <p><span className="font-medium text-foreground">Windows (PowerShell):</span> <code>powershell -c &quot;irm https://astral.sh/uv/install.ps1 | iex&quot;</code></p>
              <p className="pt-1">Add the printed directory (e.g. <code>~/.local/bin</code> or <code>%USERPROFILE%\.local\bin</code>) to your PATH and run <code>uv --version</code> to confirm.</p>
            </div>
          </li>
          <li>
            <p className="font-semibold">Download the Blender MCP addon</p>
            <div className="mt-2 space-y-2 text-xs text-muted-foreground">
              <Button asChild size="sm" className="gap-2">
                <a href="/downloads/blender-mcp-addon.py" download>
                  <Download className="h-3.5 w-3.5" />
                  Direct download
                </a>
              </Button>
              <p className="text-xs">
                or clone the upstream repository:
                <br />
                <code>git clone https://github.com/ahujasid/blender-mcp.git</code>
              </p>
              <p className="text-xs">Install via Blender → Preferences → Add-ons → Install.</p>
            </div>
          </li>
          <li>
            <p className="font-semibold">Start the bridge</p>
            <p className="mt-2 rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
              Run <code>uvx blender-mcp</code> and ensure host/port match your `.env` values.
            </p>
          </li>
          <li>
            <p className="font-semibold">Verify the connection</p>
            <p className="mt-2 rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
              Open ModelForge (web or desktop) and confirm the <em>MCP Connection</em> card shows “Connected”.
            </p>
          </li>
        </ol>
        <Button asChild variant="secondary" size="sm" className="gap-2">
          <Link href="/docs">
            View full guide
            <ExternalLink className="h-3.5 w-3.5" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  )
}
