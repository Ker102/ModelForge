import { NextResponse, type NextRequest } from "next/server"
import { z } from "zod"

import { auth } from "@/lib/auth"
import { prisma } from "@/lib/db"

const payloadSchema = z.object({
  allowHyper3dAssets: z.boolean().optional(),
  allowSketchfabAssets: z.boolean().optional(),
  allowPolyHavenAssets: z.boolean().optional(),
  allowWebResearch: z.boolean().optional(),
})

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
  const { id } = await params

  const subscriptionTier = (session.user.subscriptionTier ?? "free").toLowerCase()
  const isPaidTier = subscriptionTier === "starter" || subscriptionTier === "pro"

  const project = await prisma.project.findFirst({
    where: {
      id,
      userId: session.user.id,
      isDeleted: false,
    },
    select: { id: true },
  })

  if (!project) {
    return NextResponse.json({ error: "Project not found" }, { status: 404 })
  }

  let body: unknown
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: "Invalid JSON payload" }, { status: 400 })
  }

  const parsed = payloadSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json(
      {
        error: "Invalid payload",
        details: parsed.error.flatten(),
      },
      { status: 400 }
    )
  }

  const {
    allowHyper3dAssets,
    allowSketchfabAssets,
    allowPolyHavenAssets,
    allowWebResearch,
  } = parsed.data
  if (!isPaidTier && allowWebResearch === true) {
    return NextResponse.json(
      { error: "Upgrade required to enable web research." },
      { status: 403 }
    )
  }

  if (
    allowHyper3dAssets === undefined &&
    allowSketchfabAssets === undefined &&
    allowPolyHavenAssets === undefined &&
    allowWebResearch === undefined
  ) {
    return NextResponse.json(
      { error: "No recognized settings provided" },
      { status: 400 }
    )
  }

  const updated = await prisma.project.update({
    where: { id },
    data: {
      ...(allowHyper3dAssets !== undefined
        ? { allowHyper3dAssets }
        : {}),
      ...(allowSketchfabAssets !== undefined
        ? { allowSketchfabAssets }
        : {}),
      ...(allowPolyHavenAssets !== undefined
        ? { allowPolyHavenAssets }
        : {}),
      ...(allowWebResearch !== undefined
        ? { allowWebResearch }
        : {}),
    },
    select: {
      allowHyper3dAssets: true,
      allowSketchfabAssets: true,
      allowPolyHavenAssets: true,
      allowWebResearch: true,
    },
  })

  return NextResponse.json(updated)
}
