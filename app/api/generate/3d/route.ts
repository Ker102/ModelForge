
import { NextRequest, NextResponse } from "next/server";
import { generate3D } from "@/lib/generation/service";
import { GenerationRequest } from "@/lib/generation/client";

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { prompt, image_url, model_type } = body;

        if (!prompt && !image_url) {
            return NextResponse.json(
                { error: "Prompt or Image URL is required" },
                { status: 400 }
            );
        }

        if (!model_type) {
            return NextResponse.json(
                { error: "Model type is required (hunyuan | trellis)" },
                { status: 400 }
            );
        }

        const request: GenerationRequest = {
            prompt,
            image_url,
            model_type
        };

        const result = await generate3D(request);

        if (result.status === 'failed') {
            return NextResponse.json({ error: result.error }, { status: 500 });
        }

        return NextResponse.json(result);

    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || "Internal Server Error" },
            { status: 500 }
        );
    }
}
