import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { updateSession } from "@/lib/supabase/middleware"

export const runtime = "nodejs"

export default async function middleware(req: NextRequest) {
  const pathname = req.nextUrl.pathname

  // Debug logging for OAuth troubleshooting
  const cookies = req.cookies.getAll()
  const authCookies = cookies.filter(c => c.name.includes('auth-token'))
  console.log(`[Middleware] ${pathname} - Auth cookies present: ${authCookies.length > 0}`, authCookies.map(c => c.name))

  // Update Supabase session
  const { supabaseResponse, user } = await updateSession(req)
  const isLoggedIn = !!user

  console.log(`[Middleware] ${pathname} - User logged in: ${isLoggedIn}`, user?.email || 'none')

  const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/signup")
  const isDashboard = pathname.startsWith("/dashboard")
  const isSetupPage = pathname.startsWith("/setup")

  // Redirect logged-in users away from auth pages
  if (isAuthPage) {
    if (isLoggedIn) {
      return NextResponse.redirect(new URL("/dashboard", req.url))
    }
    return supabaseResponse
  }

  // Protect dashboard routes
  if (isDashboard && !isLoggedIn) {
    console.log(`[Middleware] Redirecting unauthenticated user from dashboard to login`)
    return NextResponse.redirect(new URL("/login", req.url))
  }

  // Allow setup page without auth (for addon installation)
  if (isSetupPage) {
    return supabaseResponse
  }

  return supabaseResponse
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}

