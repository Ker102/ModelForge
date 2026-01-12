"use client";

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Box, Wand2 } from "lucide-react";
import { ModelViewer } from "./ModelViewer";
import { GenerationResponse } from "@/lib/generation/client";

export function GenerationPanel() {
    const [prompt, setPrompt] = useState("");
    const [modelType, setModelType] = useState<"hunyuan" | "trellis">("hunyuan");
    const [isGenerating, setIsGenerating] = useState(false);
    const [result, setResult] = useState<GenerationResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt || isGenerating) return;

        setIsGenerating(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch("/api/generate/3d", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt,
                    model_type: modelType
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Generation failed");
            }

            setResult(data);
        } catch (err: unknown) {
            console.error(err);
            setError(err instanceof Error ? err.message : "An unknown error occurred");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !isGenerating) {
            e.preventDefault();
            handleGenerate();
        }
    };

    // Safe output URL extraction with null-safety
    const outputUrl: string | null = (() => {
        if (!result?.output) return null;
        if (typeof result.output === 'string') return result.output;
        if (Array.isArray(result.output) && result.output.length > 0) {
            return result.output[0];
        }
        return null;
    })();

    return (
        <div className="space-y-6">
            <Card className="w-full max-w-2xl mx-auto">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Wand2 className="w-5 h-5 text-purple-500" />
                        AI 3D Generator
                    </CardTitle>
                    <CardDescription>
                        Generate high-quality 3D assets using state-of-the-art models.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <label htmlFor="model-selection" className="text-sm font-medium">
                            Model Selection
                        </label>
                        <select
                            id="model-selection"
                            value={modelType}
                            onChange={(e) => setModelType(e.target.value as "hunyuan" | "trellis")}
                            className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <option value="hunyuan">
                                Hunyuan3D-2 (Tencent) - Best for organic shapes &amp; characters
                            </option>
                            <option value="trellis">
                                Microsoft TRELLIS - Best for hard-surface &amp; geometry
                            </option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label htmlFor="prompt-input" className="text-sm font-medium">
                            Prompt
                        </label>
                        <div className="flex gap-2">
                            <Input
                                id="prompt-input"
                                placeholder="A futuristic sci-fi helmet..."
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                onKeyDown={handleKeyDown}
                                maxLength={1000}
                                aria-describedby="prompt-hint"
                            />
                            <Button onClick={handleGenerate} disabled={isGenerating || !prompt}>
                                {isGenerating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Box className="w-4 h-4 mr-2" />}
                                Generate
                            </Button>
                        </div>
                        <p id="prompt-hint" className="text-xs text-muted-foreground">
                            Max 1000 characters
                        </p>
                    </div>

                    {error && (
                        <div className="p-4 bg-red-500/10 text-red-500 rounded-md text-sm border border-red-500/20" role="alert">
                            {error}
                        </div>
                    )}
                </CardContent>
            </Card>

            {outputUrl && (
                <Card className="w-full max-w-2xl mx-auto border-purple-500/50">
                    <CardHeader>
                        <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">Generation Result</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ModelViewer url={outputUrl} />
                    </CardContent>
                    <CardFooter className="justify-between">
                        <span className="text-xs text-muted-foreground">ID: {result?.id}</span>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(outputUrl, '_blank')}
                        >
                            Download GLB
                        </Button>
                    </CardFooter>
                </Card>
            )}
        </div>
    );
}
