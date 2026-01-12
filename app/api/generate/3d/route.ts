
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { generate3D } from "@/lib/generation/service";
import { GenerationRequest } from "@/lib/generation/client";

// Constants
const MAX_PROMPT_LENGTH = 1000;
const VALID_MODEL_TYPES = ["hunyuan", "trellis"] as const;

// Simple in-memory rate limiter (use Redis in production for multi-instance)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();
const RATE_LIMIT_WINDOW_MS = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 10; // 10 requests per minute

function getRateLimitKey(req: NextRequest): string {
    const forwarded = req.headers.get("x-forwarded-for");
    const ip = forwarded ? forwarded.split(",")[0].trim() : "unknown";
    return `ratelimit:${ip}`;
}

function checkRateLimit(key: string): { allowed: boolean; remaining: number } {
    const now = Date.now();
    const entry = rateLimitMap.get(key);

    if (!entry || now > entry.resetTime) {
        rateLimitMap.set(key, { count: 1, resetTime: now + RATE_LIMIT_WINDOW_MS });
        return { allowed: true, remaining: RATE_LIMIT_MAX_REQUESTS - 1 };
    }

    if (entry.count >= RATE_LIMIT_MAX_REQUESTS) {
        return { allowed: false, remaining: 0 };
    }

    entry.count++;
    return { allowed: true, remaining: RATE_LIMIT_MAX_REQUESTS - entry.count };
}

function isValidUrl(urlString: string): boolean {
    try {
        const url = new URL(urlString);
        return url.protocol === "https:" || url.protocol === "http:";
    } catch {
        return false;
    }
}

export async function POST(req: NextRequest) {
    try {
        // 1. Authentication check
        const session = await auth();
        if (!session?.user) {
            console.warn("Unauthorized access attempt to /api/generate/3d");
            return NextResponse.json(
                { error: "Authentication required" },
                { status: 401 }
            );
        }

        // 2. Rate limiting
        const rateLimitKey = getRateLimitKey(req);
        const { allowed, remaining } = checkRateLimit(rateLimitKey);
        if (!allowed) {
            console.warn(`Rate limit exceeded for ${rateLimitKey}`);
            return NextResponse.json(
                { error: "Rate limit exceeded. Please try again later." },
                { status: 429 }
            );
        }

        const body = await req.json();
        const { prompt, image_url, model_type } = body;

        // 3. Input validation - prompt or image_url required
        if (!prompt && !image_url) {
            return NextResponse.json(
                { error: "Prompt or Image URL is required" },
                { status: 400 }
            );
        }

        // 4. Validate prompt length
        if (prompt && prompt.length > MAX_PROMPT_LENGTH) {
            return NextResponse.json(
                { error: `Prompt exceeds maximum length of ${MAX_PROMPT_LENGTH} characters` },
                { status: 400 }
            );
        }

        // 5. Validate image_url format
        if (image_url && !isValidUrl(image_url)) {
            return NextResponse.json(
                { error: "Invalid image URL format. Must be a valid HTTP/HTTPS URL." },
                { status: 400 }
            );
        }

        // 6. Validate model_type
        if (!model_type) {
            return NextResponse.json(
                { error: "Model type is required (hunyuan | trellis)" },
                { status: 400 }
            );
        }

        if (!VALID_MODEL_TYPES.includes(model_type)) {
            return NextResponse.json(
                { error: `Invalid model_type: "${model_type}". Allowed values: hunyuan, trellis` },
                { status: 400 }
            );
        }

        const request: GenerationRequest = {
            prompt,
            image_url,
            model_type
        };

        const result = await generate3D(request);

        // 7. Use 422 for generation failures (client/validation issue, not server error)
        if (result.status === 'failed') {
            return NextResponse.json({ error: result.error }, { status: 422 });
        }

        return NextResponse.json(result, {
            headers: { "X-RateLimit-Remaining": remaining.toString() }
        });

    } catch (error: unknown) {
        // 8. Log full error server-side, return generic message to client
        console.error("3D Generation API Error:", error);
        return NextResponse.json(
            { error: "Internal Server Error" },
            { status: 500 }
        );
    }
}
