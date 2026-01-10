
"use client";

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Box, Wand2, RefreshCw } from "lucide-react";
import { ModelViewer } from "./ModelViewer";

export function GenerationPanel() {
    const [prompt, setPrompt] = useState("");
    const [modelType, setModelType] = useState<"hunyuan" | "trellis">("hunyuan");
    const [isGenerating, setIsGenerating] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt) return;

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
        } catch (err: any) {
            console.error(err);
            setError(err.message);
        } finally {
            setIsGenerating(false);
        }
    };

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
                        <label className="text-sm font-medium">Model Selection</label>
                        <Select value={modelType} onValueChange={(v: any) => setModelType(v)}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select Model" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="hunyuan">
                                    <div className="flex flex-col">
                                        <span className="font-semibold">Hunyuan3D-2 (Tencent)</span>
                                        <span className="text-xs text-muted-foreground">Best for organic shapes & characters. High detail.</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="trellis">
                                    <div className="flex flex-col">
                                        <span className="font-semibold">Microsoft TRELLIS</span>
                                        <span className="text-xs text-muted-foreground">Best for hard-surface & geometry. Fast inference.</span>
                                    </div>
                                </SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Prompt</label>
                        <div className="flex gap-2">
                            <Input
                                placeholder="A futuristic sci-fi helmet..."
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                            />
                            <Button onClick={handleGenerate} disabled={isGenerating || !prompt}>
                                {isGenerating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Box className="w-4 h-4 mr-2" />}
                                Generate
                            </Button>
                        </div>
                    </div>

                    {error && (
                        <div className="p-4 bg-red-500/10 text-red-500 rounded-md text-sm border border-red-500/20">
                            {error}
                        </div>
                    )}
                </CardContent>
            </Card>

            {result && result.output && (
                <Card className="w-full max-w-2xl mx-auto border-purple-500/50">
                    <CardHeader>
                        <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">Generation Result</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {/* Note: The 'output' structure depends on the specific Replicate model response. 
                 Usually it's a URL string or an array of URL strings. 
                 Adjusting logic to handle common Replicate output formats. 
             */}
                        <ModelViewer url={typeof result.output === 'string' ? result.output : result.output[0]} />
                    </CardContent>
                    <CardFooter className="justify-between">
                        <span className="text-xs text-muted-foreground">ID: {result.id}</span>
                        <Button variant="outline" size="sm" onClick={() => window.open(typeof result.output === 'string' ? result.output : result.output[0], '_blank')}>
                            Download GLB
                        </Button>
                    </CardFooter>
                </Card>
            )}
        </div>
    );
}
