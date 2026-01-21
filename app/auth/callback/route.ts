import { NextResponse } from "next/server"
import { createClient } from "@/lib/supabase/server"

export async function GET(request: Request) {
    const { searchParams, origin } = new URL(request.url)
    const code = searchParams.get("code")
    const next = searchParams.get("next") ?? "/dashboard"

    console.log("[Auth Callback] Code received:", code ? "yes" : "no")

    if (code) {
        const supabase = await createClient()
        const { data, error } = await supabase.auth.exchangeCodeForSession(code)

        console.log("[Auth Callback] Exchange result:", {
            success: !error,
            error: error?.message,
            user: data?.user?.email
        })

        if (!error) {
            return NextResponse.redirect(`${origin}${next}`)
        }

        // Include specific error in redirect
        return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(error.message)}`)
    }

    console.log("[Auth Callback] No code provided")
    return NextResponse.redirect(`${origin}/login?error=NoCodeProvided`)
}
