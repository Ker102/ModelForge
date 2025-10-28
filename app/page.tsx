import { auth } from "@/lib/auth"
import { Navbar } from "@/components/landing/navbar"
import { Hero } from "@/components/landing/hero"
import { Features } from "@/components/landing/features"
import { Pricing } from "@/components/landing/pricing"
import { Footer } from "@/components/landing/footer"

export default async function Home() {
  const session = await auth()
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Features />
        <Pricing
          isAuthenticated={Boolean(session?.user)}
          currentTier={session?.user?.subscriptionTier ?? null}
        />
      </main>
      <Footer />
    </div>
  )
}
