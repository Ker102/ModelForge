"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { signIn } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"
type LoginFormProps = {
  initialErrorCode?: string
  callbackUrl?: string
}

const ERROR_MESSAGES: Record<string, { message: string; allowOAuthRetry?: boolean }> = {
  OAuthAccountNotLinked: {
    message:
      "That Google account is already linked to a different login method. Sign in with email/password or contact support to merge accounts.",
    allowOAuthRetry: true,
  },
  OAuthSignin: {
    message: "Google sign-in was cancelled. Try again with the correct account.",
    allowOAuthRetry: true,
  },
  OAuthCallback: {
    message: "We couldn’t complete Google sign-in. Try again or choose another Google account.",
    allowOAuthRetry: true,
  },
  OAuthCreateAccount: {
    message: "We couldn’t create your Google-linked account. Please try again.",
    allowOAuthRetry: true,
  },
  Configuration: {
    message: "Google sign-in is misconfigured. Please try email/password or reach out to support while we fix this.",
    allowOAuthRetry: false,
  },
}

function getErrorMessage(code?: string) {
  if (!code) return { message: null, allowOAuthRetry: false }
  const mapped = ERROR_MESSAGES[code] ?? {
    message: "Unable to sign in with Google. Please try again or use email/password.",
    allowOAuthRetry: true,
  }
  return mapped
}

export function LoginForm({ initialErrorCode, callbackUrl }: LoginFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [isOAuthLoading, setIsOAuthLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showOAuthRetry, setShowOAuthRetry] = useState(false)

  useEffect(() => {
    if (!initialErrorCode) {
      setShowOAuthRetry(false)
      return
    }
    const { message, allowOAuthRetry } = getErrorMessage(initialErrorCode)
    if (message) {
      setError(message)
      setShowOAuthRetry(Boolean(allowOAuthRetry))
    }
  }, [initialErrorCode])

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoading(true)
    setError(null)
    setShowOAuthRetry(false)

    const formData = new FormData(event.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    const targetUrl = callbackUrl ?? "/dashboard"

    try {
      const result = await signIn("credentials", {
        email,
        password,
        redirect: false,
        callbackUrl: targetUrl,
      })

      if (result?.error) {
        setError("Invalid email or password")
      } else {
        router.push(targetUrl)
        router.refresh()
      }
    } catch (error) {
      setError("An error occurred. Please try again.")
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleGoogleSignIn() {
    setError(null)
    setIsOAuthLoading(true)
    setShowOAuthRetry(false)
    try {
      const targetUrl = callbackUrl ?? "/dashboard"
      await signIn("google", {
        callbackUrl: targetUrl,
        prompt: "select_account",
      })
    } catch (error) {
      console.error(error)
      setError("Failed to sign in with Google. Please try again.")
      setShowOAuthRetry(true)
    } finally {
      setIsOAuthLoading(false)
    }
  }

  return (
    <div className="grid gap-6">
      <form onSubmit={onSubmit}>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              placeholder="name@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              disabled={isLoading}
              required
            />
          </div>
          {error && (
            <div className="text-sm text-destructive">{error}</div>
          )}
          <Button disabled={isLoading || isOAuthLoading}>
            {isLoading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Signing in...
              </span>
            ) : (
              "Sign in with email"
            )}
          </Button>
        </div>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <Button
        type="button"
        variant="outline"
        onClick={handleGoogleSignIn}
        disabled={isOAuthLoading || isLoading}
      >
        {isOAuthLoading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <svg
            className="mr-2 h-4 w-4"
            aria-hidden="true"
            focusable="false"
            viewBox="0 0 24 24"
          >
            <path
              fill="#EA4335"
              d="M12 10.2v3.6h5.1c-.2 1.1-.9 2.5-2.1 3.5l3.2 2.5c1.9-1.8 3-4.3 3-7.4 0-.7-.1-1.4-.2-2H12z"
            />
            <path
              fill="#34A853"
              d="M5.9 14.1c-.3-.9-.5-1.9-.5-3s.2-2.1.5-3l-3.3-2.6C1.4 7 1 8.9 1 11.1c0 2.1.4 4.1 1.6 5.7l3.3-2.7z"
            />
            <path
              fill="#4A90E2"
              d="M12 21c2.7 0 5-1 6.6-2.7l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.7-5.6-4L3.1 16c1.3 2.6 4 5 8.9 5z"
            />
            <path
              fill="#FBBC05"
              d="M12 4.6c1.5 0 2.9.5 4 1.4L19 2.9C17.5 1.5 15.1 1 12 1 7 1 4.3 3.4 3.1 6.2l3.5 2.8c.8-2.3 3-4.4 5.4-4.4z"
            />
          </svg>
        )}
        Continue with Google
      </Button>

      {showOAuthRetry && (
        <div className="flex flex-col gap-2">
          <Button
            type="button"
            variant="ghost"
            onClick={handleGoogleSignIn}
            disabled={isOAuthLoading}
          >
            Use a different Google account
          </Button>
          <p className="text-xs text-muted-foreground text-center">
            This takes you back to Google&apos;s account picker so you can choose another address.
          </p>
        </div>
      )}
    </div>
  )
}
