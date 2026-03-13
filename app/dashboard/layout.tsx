import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"
import { SessionMonitor } from "@/components/auth/session-monitor"

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth()

  if (!session) {
    redirect("/login")
  }

  return (
    <div className="flex min-h-screen flex-col">
      <SessionMonitor />
      <DashboardNav user={session.user} />
      <main className="flex-1">{children}</main>
    </div>
  )
}

