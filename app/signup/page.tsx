import Link from "next/link"
import { redirect } from "next/navigation"
import { auth } from "@/lib/auth"
import { SignupForm } from "@/components/auth/signup-form"
import { Hammer } from "lucide-react"

export default async function SignupPage() {
  const session = await auth()
  
  if (session) {
    redirect("/dashboard")
  }

  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <Link href="/" className="mb-8 flex items-center gap-2">
        <Hammer className="h-6 w-6 text-primary" />
        <span className="text-xl font-bold">ModelForge</span>
      </Link>
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">
            Create an account
          </h1>
          <p className="text-sm text-muted-foreground">
            Enter your email below to create your account
          </p>
        </div>
        <SignupForm />
        <p className="px-8 text-center text-sm text-muted-foreground">
          <Link
            href="/login"
            className="hover:text-brand underline underline-offset-4"
          >
            Already have an account? Sign In
          </Link>
        </p>
      </div>
    </div>
  )
}

