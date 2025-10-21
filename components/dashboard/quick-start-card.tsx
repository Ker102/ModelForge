"use client"

import Link from "next/link"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ExternalLink } from "lucide-react"

export function QuickStartCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Start</CardTitle>
        <CardDescription>Everything you need before connecting Blender</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <ol className="space-y-2 list-decimal list-inside">
          <li>Install Blender 3.0+ and Python 3.10+.</li>
          <li>
            Install the <strong>uv</strong> package manager:
            <ul className="mt-1 space-y-1 list-disc list-inside pl-4 text-xs text-muted-foreground">
              <li>
                Linux: <code>curl -LsSf https://astral.sh/uv/install.sh | sh</code>
              </li>
              <li>
                macOS: <code>brew install uv</code> (or use the Linux script)
              </li>
              <li>
                Windows (PowerShell):{" "}
                <code>powershell -c &quot;irm https://astral.sh/uv/install.ps1 | iex&quot;</code>
              </li>
            </ul>
          </li>
          <li>Download the latest Blender MCP addon (`addon.py`) and install it via Blender &gt; Preferences &gt; Add-ons.</li>
          <li>Run the MCP bridge: <code>uvx blender-mcp</code> (host/port must match your `.env`).</li>
          <li>
            Open ModelForge (web or desktop), sign in, and confirm the <em>MCP Connection</em> card shows “Connected”.
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
