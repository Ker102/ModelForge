import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { ProjectList } from "@/components/dashboard/project-list"
import { CreateProjectButton } from "@/components/dashboard/create-project-button"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export default async function DashboardPage() {
  const session = await auth()
  
  if (!session?.user) {
    return null
  }

  const projects = await prisma.project.findMany({
    where: {
      userId: session.user.id,
      isDeleted: false,
    },
    orderBy: {
      lastModified: "desc",
    },
  })

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
      <ProjectList projects={projects} />
    </div>
  )
}

