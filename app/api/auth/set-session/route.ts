import { createServerClient } from "@supabase/ssr"
import { NextRequest, NextResponse } from "next/server"

/**
 * API route that sets Supabase session from tokens.
 * Called by Electron after receiving OAuth tokens to ensure
 * cookies are properly set for server-side validation.
 */
export async function POST(request: NextRequest) {
    try {
        const { access_token, refresh_token } = await request.json()

        if (!access_token || !refresh_token) {
            return NextResponse.json(
                { error: "Missing tokens" },
                { status: 400 }
            )
        }

        // Create the response first so we can set cookies on it
        const response = NextResponse.json({ success: true })

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
                            // Set cookies on the response
                            response.cookies.set(name, value, {
                                ...options,
                                // Ensure cookies work in development
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

        // Set the session using the tokens
        const { data, error } = await supabase.auth.setSession({
            access_token,
            refresh_token,
        })

        if (error) {
            console.error("[API] Failed to set session:", error)
            return NextResponse.json(
                { error: error.message },
                { status: 500 }
            )
        }

        console.log("[API] Session set successfully for user:", data.user?.email)
        console.log("[API] Cookies set:", response.cookies.getAll().map(c => c.name))

        return response
    } catch (err) {
        console.error("[API] Error in set-session:", err)
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        )
    }
}

