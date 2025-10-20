import { MessageSquare, Zap, Brain, Database, Eye, Workflow } from "lucide-react"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const features = [
  {
    icon: MessageSquare,
    title: "Natural Language Control",
    description: "Create and modify 3D models using simple text commands. No scripting required.",
  },
  {
    icon: Brain,
    title: "AI-Powered Understanding",
    description: "Advanced AI comprehends your intent and generates precise Blender operations.",
  },
  {
    icon: Database,
    title: "Project Memory",
    description: "AI remembers your project context across sessions for seamless continuity.",
  },
  {
    icon: Eye,
    title: "Viewport Awareness",
    description: "AI can see your scene and provide contextual suggestions and modifications.",
  },
  {
    icon: Workflow,
    title: "MCP Integration",
    description: "Direct integration with Blender's Model Context Protocol for reliable execution.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Real-time responses and instant command execution in your Blender workspace.",
  },
]

export function Features() {
  return (
    <section id="features" className="container py-20 md:py-32 bg-muted/50">
      <div className="mx-auto max-w-6xl">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold">Powerful Features</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to supercharge your 3D modeling workflow
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card key={feature.title} className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <feature.icon className="h-10 w-10 text-primary mb-2" />
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

