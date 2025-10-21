import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"

export function Hero() {
  return (
    <section className="container py-20 md:py-32">
      <div className="mx-auto max-w-4xl text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border bg-muted/50 text-sm">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>Transform your Blender workflow with AI</span>
        </div>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          Build 3D Models with
          <span className="text-primary"> Natural Language</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          ModelForge brings AI-powered automation to Blender. Create, modify, and enhance your 3D projects through simple conversation.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/signup">
            <Button size="lg" className="gap-2">
              Start Free Trial
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/docs">
            <Button size="lg" variant="outline">
              Quick Start Guide
            </Button>
          </Link>
        </div>
        <div className="pt-8">
          <div className="relative rounded-lg border bg-muted/50 p-2">
            <div className="aspect-video rounded-md bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
              <p className="text-sm text-muted-foreground">Product Demo Video/Screenshot</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
