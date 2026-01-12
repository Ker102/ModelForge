import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { GenerationPanel } from "@/components/generation/GenerationPanel";
import { ErrorBoundary } from "@/components/generation/ErrorBoundary";

export default async function GeneratePage() {
    // Server-side auth protection
    const session = await auth();

    if (!session?.user) {
        redirect("/login");
    }

    return (
        <div className="container mx-auto py-10">
            <div className="mb-8 text-center">
                <h1 className="text-4xl font-bold tracking-tight mb-2">3D Generation Studio</h1>
                <p className="text-muted-foreground">
                    Create game-ready assets using SOTA AI models Hunyuan3D and TRELLIS.
                </p>
            </div>
            <ErrorBoundary fallbackTitle="3D Generation Error">
                <GenerationPanel />
            </ErrorBoundary>
        </div>
    );
}
