/**
 * Brave Search Integration
 *
 * Provides web search capabilities as a fallback knowledge source
 * when RAG retrieval doesn't have sufficient coverage.
 *
 * Env vars:
 *  - BRAVE_API_KEY (required)
 *
 * API docs: https://api.search.brave.com/app/documentation/web-search/query
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface BraveSearchResult {
    title: string
    url: string
    description: string
}

export interface BraveSearchResponse {
    results: BraveSearchResult[]
    query: string
    totalResults: number
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

const BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"

/**
 * Search the web using Brave Search API.
 *
 * @param query - Search query string
 * @param options - Optional count and offset
 * @returns Search results with title, URL, and description
 */
export async function braveSearch(
    query: string,
    options: { count?: number; offset?: number; freshness?: string } = {}
): Promise<BraveSearchResponse> {
    const apiKey = process.env.BRAVE_API_KEY
    if (!apiKey) {
        throw new Error("BRAVE_API_KEY environment variable is not set")
    }

    const params = new URLSearchParams({
        q: query,
        count: String(options.count ?? 5),
        offset: String(options.offset ?? 0),
    })

    if (options.freshness) {
        params.set("freshness", options.freshness)
    }

    const response = await fetch(`${BRAVE_API_URL}?${params}`, {
        headers: {
            Accept: "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": apiKey,
        },
    })

    if (!response.ok) {
        throw new Error(`Brave Search API error: ${response.status} ${response.statusText}`)
    }

    const data = await response.json() as {
        web?: {
            results?: Array<{
                title?: string
                url?: string
                description?: string
            }>
        }
        query?: { original?: string }
    }

    const webResults = data.web?.results ?? []

    return {
        results: webResults.map((r) => ({
            title: r.title ?? "",
            url: r.url ?? "",
            description: r.description ?? "",
        })),
        query: data.query?.original ?? query,
        totalResults: webResults.length,
    }
}

/**
 * Search for Blender-specific technical information.
 * Adds "Blender Python API" context to improve result relevance.
 */
export async function braveSearchBlender(
    query: string,
    options: { count?: number } = {}
): Promise<BraveSearchResponse> {
    return braveSearch(`Blender Python API ${query}`, {
        count: options.count ?? 5,
        freshness: "py", // past year — ensures up-to-date results
    })
}
