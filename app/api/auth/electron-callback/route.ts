import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"
import { NextRequest, NextResponse } from "next/server"

/**
 * Server-side OAuth callback handler for Electron
 * 
 * This route:
 * 1. Receives the OAuth code from Supabase
 * 2. Exchanges it for session tokens (server-side, with access to PKCE cookies)
 * 3. Redirects to modelforge:// deep link with tokens
 */
export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get("code")
    const error = requestUrl.searchParams.get("error")
    const errorDescription = requestUrl.searchParams.get("error_description")

    const origin = requestUrl.origin

    // Handle OAuth errors
    if (error) {
        const errorPage = new URL("/auth/electron-callback", origin)
        errorPage.searchParams.set("error", error)
        errorPage.searchParams.set("error_description", errorDescription || "Authentication failed")
        return NextResponse.redirect(errorPage)
    }

    if (!code) {
        const errorPage = new URL("/auth/electron-callback", origin)
        errorPage.searchParams.set("error", "no_code")
        errorPage.searchParams.set("error_description", "No authorization code received")
        return NextResponse.redirect(errorPage)
    }

    // Create server-side Supabase client with cookie access
    const cookieStore = await cookies()
    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll()
                },
                setAll(cookiesToSet) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) =>
                            cookieStore.set(name, value, options)
                        )
                    } catch {
                        // Ignore errors in certain contexts
                    }
                },
            },
        }
    )

    try {
        // Exchange the code for a session
        const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)

        if (exchangeError) {
            const errorPage = new URL("/auth/electron-callback", origin)
            errorPage.searchParams.set("error", "exchange_failed")
            errorPage.searchParams.set("error_description", exchangeError.message)
            return NextResponse.redirect(errorPage)
        }

        if (data.session) {
            // Success! Redirect to the callback page with tokens
            const successPage = new URL("/auth/electron-callback", origin)
            successPage.searchParams.set("success", "true")
            successPage.searchParams.set("access_token", data.session.access_token)
            successPage.searchParams.set("refresh_token", data.session.refresh_token)
            return NextResponse.redirect(successPage)
        }

        // No session returned
        const errorPage = new URL("/auth/electron-callback", origin)
        errorPage.searchParams.set("error", "no_session")
        errorPage.searchParams.set("error_description", "No session was created")
        return NextResponse.redirect(errorPage)

    } catch (err) {
        console.error("[OAuth] Exchange error:", err)
        const errorPage = new URL("/auth/electron-callback", origin)
        errorPage.searchParams.set("error", "unexpected")
        errorPage.searchParams.set("error_description", "An unexpected error occurred")
        return NextResponse.redirect(errorPage)
    }
}
