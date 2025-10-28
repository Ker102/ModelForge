const FIRECRAWL_ENDPOINT =
  process.env.FIRECRAWL_API_BASE_URL?.replace(/\/+$/, "") ?? "https://api.firecrawl.dev"

interface FirecrawlApiResult {
  title?: string
  url?: string
  snippet?: string
  content?: string
}

export interface FirecrawlSearchResult {
  query: string
  results: Array<{
    title: string
    url: string
    snippet: string
  }>
}

export async function searchFirecrawl(query: string): Promise<FirecrawlSearchResult | null> {
  const apiKey = process.env.FIRECRAWL_API_KEY
  if (!apiKey) {
    return null
  }

  try {
    const response = await fetch(`${FIRECRAWL_ENDPOINT}/v1/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({ query, limit: 5 }),
      signal: AbortSignal.timeout(12_000),
    })

    if (!response.ok) {
      const errorBody = await response.text().catch(() => "")
      console.error("Firecrawl search failed:", response.status, errorBody)
      return null
    }

    const data = (await response.json().catch(() => null)) as
      | { results?: FirecrawlApiResult[] }
      | null

    if (!data?.results || !Array.isArray(data.results)) {
      return null
    }

    const results = data.results
      .filter((item) => item?.url)
      .slice(0, 5)
      .map((item) => ({
        title: item.title?.trim() ?? item.url ?? "Untitled result",
        url: item.url ?? "",
        snippet: item.snippet?.trim() ?? item.content?.slice(0, 180) ?? "",
      }))
      .filter((item) => item.url)

    if (results.length === 0) {
      return null
    }

    return {
      query,
      results,
    }
  } catch (error) {
    console.error("Firecrawl request error:", error)
    return null
  }
}
