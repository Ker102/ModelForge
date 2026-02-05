import { createServerClient } from "@supabase/ssr"
import { NextRequest, NextResponse } from "next/server"

/**
 * API route that sets Supabase session AND redirects to dashboard.
 * This ensures cookies are set in the same response as the redirect,
 * solving the timing issue where fetch cookies aren't processed before redirect.
 */
export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams
    const accessToken = searchParams.get("access_token")
    const refreshToken = searchParams.get("refresh_token")
    const redirectTo = searchParams.get("redirect") || "/dashboard"

    if (!accessToken || !refreshToken) {
        console.error("[API] Missing tokens in set-session-redirect")
        return NextResponse.redirect(new URL("/login?error=missing_tokens", request.url))
    }

    // Use the origin from the request headers to ensure cookies work
    // This fixes the 127.0.0.1 vs localhost mismatch in Electron
    const origin = request.headers.get("origin") || request.headers.get("referer")?.split("/").slice(0, 3).join("/") || "http://127.0.0.1:3000"
    const redirectUrl = new URL(redirectTo, origin)

    console.log("[API] Redirecting to:", redirectUrl.toString(), "Origin:", origin)

    const response = NextResponse.redirect(redirectUrl)

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll()
                },
                setAll(cookiesToSet) {
                    cookiesToSet.forEach(({ name, value, options }) => {
                        // Set cookies on the redirect response
                        response.cookies.set(name, value, {
                            ...options,
                            sameSite: "lax",
                            secure: process.env.NODE_ENV === "production",
                            httpOnly: true,
                            path: "/",
                        })
                    })
                },
            },
        }
    )

    try {
        // Set the session using the tokens
        const { data, error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
        })

        if (error) {
            console.error("[API] Failed to set session:", error)
            return NextResponse.redirect(
                new URL(`/login?error=${encodeURIComponent(error.message)}`, request.url)
            )
        }

        console.log("[API] Session set and redirecting for user:", data.user?.email)
        console.log("[API] Cookies set:", response.cookies.getAll().map(c => c.name))

        return response
    } catch (err) {
        console.error("[API] Error in set-session-redirect:", err)
        return NextResponse.redirect(new URL("/login?error=internal_error", request.url))
    }
}
