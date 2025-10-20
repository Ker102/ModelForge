import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { z } from "zod"

const createProjectSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  blenderVersion: z.string().optional(),
})

export async function GET() {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
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

    return NextResponse.json({ projects })
  } catch (error) {
    console.error("Get projects error:", error)
    return NextResponse.json(
      { error: "Failed to fetch projects" },
      { status: 500 }
    )
  }
}

export async function POST(req: Request) {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await req.json()
    const { name, description, blenderVersion } = createProjectSchema.parse(body)

    // Check project limit based on subscription tier
    const userProjects = await prisma.project.count({
      where: {
        userId: session.user.id,
        isDeleted: false,
      },
    })

    const limits: Record<string, number> = {
      free: 1,
      starter: 10,
      pro: -1, // unlimited
    }

    const maxProjects = limits[session.user.subscriptionTier] ?? 1

    if (maxProjects !== -1 && userProjects >= maxProjects) {
      return NextResponse.json(
        { error: `Project limit reached. Upgrade to create more projects.` },
        { status: 403 }
      )
    }

    const project = await prisma.project.create({
      data: {
        userId: session.user.id,
        name,
        description,
        blenderVersion,
      },
    })

    return NextResponse.json({ project }, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Invalid input data" },
        { status: 400 }
      )
    }

    console.error("Create project error:", error)
    return NextResponse.json(
      { error: "Failed to create project" },
      { status: 500 }
    )
  }
}

