# ModelForge 3D Pipeline Strategy

> Research Date: 2026-02-17 | Sources: top3d.ai, BlenderHub, Hyper3D API docs, Tripo API docs, Meta AI, 3D-Agent

## Top3D.ai Leaderboard (Community Ratings)

| Rank | Tool | Score | Price | Key Features |
|------|------|-------|-------|-------------|
| 1 | **Tripo AI** | 4.2 | $19.90/mo | Full pipeline: model→texture→retopo→rig. One-click rigging |
| 2 | **Hunyuan 3D** | 4.0 | Free (20/day) | Open-source, AI retopology, AI texturing, AI rigging |
| 3 | **Sparc3D (Hitem3D)** | 4.0 | $19.90/mo | 4K texture, Ultra HD mesh, multi-view input |
| 4 | **Hyper3D (Rodin)** | 4.0 | $24/mo | 10B-param Gen-2, 4K textures, parts decomposition |
| 5 | **YVO3D** | 4.0 | $9.99/mo | 4K texture, polycount control |
| 6 | **Lychee** | 3.9 | Credits | Image input, 3D printing |
| 7 | **TRELLIS (Microsoft)** | 3.8 | Open Source | ComfyUI, 4K texture |
| 8 | **VARCO 3D (NCSoft)** | 3.8 | $0.22/gen | API, commercial use |
| 9 | **Prism (3D AI Studio)** | 3.4 | $14/mo | Studio, AI texturing |
| 10 | **ByteDance Seed3D** | 3.3 | $0.3/gen | API |
| 11 | **Meshy AI** | 2.8 | $20/mo | Polycount control, AI texturing |
| 12 | **SAM 3D (Meta)** | 2.6 | Free | Open source, image-to-3D reconstruction |
| 13 | **Spline AI** | N/A | $30/mo | Browser-based 3D design studio |

## Direct Competitor: 3D-Agent

- **What:** Blender AI plugin using Claude + MCP (same architecture as us!)
- **Stack:** Next.js, Vercel, Stripe, Supabase (nearly identical to ours)
- **Pricing:** Free (3/day), Starter $10/mo (100), Advanced $100/mo (1000)
- **Claims:** Clean topology, <20min workflow, exports OBJ/FBX/GLB/USDZ
- **Weakness:** Text-to-3D only. No RAG pipeline, no visual feedback, no multi-provider integration
- **Our Edge:** We have RAG (127 scripts), visual feedback loop, vision analysis, multi-step planning
