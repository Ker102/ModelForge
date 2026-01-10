
import { GenerationPanel } from "@/components/generation/GenerationPanel";

export default function GeneratePage() {
    return (
        <div className="container mx-auto py-10">
            <div className="mb-8 text-center">
                <h1 className="text-4xl font-bold tracking-tight mb-2">3D Generation Studio</h1>
                <p className="text-muted-foreground">
                    Create game-ready assets using SOTA AI models Hunyuan3D and TRELLIS.
                </p>
            </div>
            <GenerationPanel />
        </div>
    );
}
