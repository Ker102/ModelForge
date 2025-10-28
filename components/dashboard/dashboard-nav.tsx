"use client"

import Link from "next/link"
import { usePathname, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Hammer, LogOut, Settings, FolderOpen } from "lucide-react"
import { signOut } from "next-auth/react"

interface DashboardNavProps {
  user?: {
    email?: string | null
    subscriptionTier?: string | null
  }
}

export function DashboardNav({ user }: DashboardNavProps) {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const subscriptionTier = (user?.subscriptionTier || "free").toLowerCase()
  const email = user?.email ?? "Unknown user"
  const searchString = searchParams.toString()
  const currentLocation = searchString ? `${pathname}?${searchString}` : pathname
  const upgradeHref = `/dashboard/settings?section=plans&from=${encodeURIComponent(currentLocation)}#plans`

  return (
    <nav className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <Hammer className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">ModelForge</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard">
              <Button
                variant={pathname === "/dashboard" ? "secondary" : "ghost"}
                size="sm"
                className="gap-2"
              >
                <FolderOpen className="h-4 w-4" />
                Projects
              </Button>
            </Link>
            <Link href="/dashboard/settings">
              <Button
                variant={pathname === "/dashboard/settings" ? "secondary" : "ghost"}
                size="sm"
                className="gap-2"
              >
                <Settings className="h-4 w-4" />
                Settings
              </Button>
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="capitalize">
              {subscriptionTier}
            </Badge>
            {subscriptionTier === "free" && (
              <Button asChild size="sm" variant="outline">
                <Link href={upgradeHref}>Upgrade</Link>
              </Button>
            )}
          </div>
          <span className="text-sm text-muted-foreground">{email}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => signOut({ callbackUrl: "/" })}
            className="gap-2"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </div>
    </nav>
  )
}
