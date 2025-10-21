import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { ProjectList } from "@/components/dashboard/project-list"
import { CreateProjectButton } from "@/components/dashboard/create-project-button"
import { UsageSummaryCard } from "@/components/dashboard/usage-summary"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { getUsageSummary } from "@/lib/usage"
import { SubscriptionTier } from "@/lib/subscription"

export default async function DashboardPage() {
  const session = await auth()
  
  if (!session?.user) {
    return null
  }

  const tier: SubscriptionTier =
    session.user.subscriptionTier === "starter" || session.user.subscriptionTier === "pro"
      ? (session.user.subscriptionTier as SubscriptionTier)
      : "free"

  const projects = await prisma.project.findMany({
    where: {
      userId: session.user.id,
      isDeleted: false,
    },
    orderBy: {
      lastModified: "desc",
    },
  })

  const usage = await getUsageSummary(session.user.id, tier)

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">My Projects</h1>
          <p className="text-muted-foreground mt-2">
            Manage your Blender AI projects
          </p>
        </div>
        <CreateProjectButton>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </CreateProjectButton>
      </div>
      <div className="mb-8">
        <UsageSummaryCard tier={tier} usage={usage} />
      </div>
      <ProjectList projects={projects} />
    </div>
  )
}
