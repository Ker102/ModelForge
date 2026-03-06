# RunPod Serverless Deployment Guide

Deploy Hunyuan3D Paint (PBR texturing) and Hunyuan3D Part (mesh segmentation)
as RunPod Serverless endpoints for ModelForge's neural 3D pipeline.

## Architecture

```
ModelForge App → runpod-client.ts → RunPod API v2 → Docker Worker → GPU
                                                         ↓
                                                   Model Output (GLB)
                                                         ↓
                                                  RunPod Blob Storage → presigned URL
```

## Prerequisites

- [RunPod account](https://www.runpod.io/) with credits
- [Docker](https://docs.docker.com/get-docker/) installed locally
- [RunPod CLI](https://docs.runpod.io/cli/install) (optional, for faster deploys)

## Step 1: Build Docker Images

### Hunyuan Paint (PBR Texturing)

```bash
cd deploy/runpod/hunyuan-paint

# Build the image (includes model weight download — may take 10-15 min)
docker build -t hunyuan-paint-worker .

# Tag for Docker Hub (replace YOUR_DOCKERHUB_USER)
docker tag hunyuan-paint-worker YOUR_DOCKERHUB_USER/hunyuan-paint-worker:latest

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USER/hunyuan-paint-worker:latest
```

### Hunyuan Part (Mesh Segmentation)

```bash
cd deploy/runpod/hunyuan-part

docker build -t hunyuan-part-worker .
docker tag hunyuan-part-worker YOUR_DOCKERHUB_USER/hunyuan-part-worker:latest
docker push YOUR_DOCKERHUB_USER/hunyuan-part-worker:latest
```

## Step 2: Create RunPod Serverless Endpoints

### Via RunPod Console (web UI)

1. Go to [console.runpod.io/serverless](https://www.runpod.io/console/serverless)
2. Click **"New Endpoint"**

#### Hunyuan Paint Endpoint

| Setting | Value |
|---------|-------|
| **Name** | `modelforge-hunyuan-paint` |
| **Docker Image** | `YOUR_DOCKERHUB_USER/hunyuan-paint-worker:latest` |
| **GPU Type** | A5000 (24GB) or A6000 (48GB) |
| **Min Workers** | `0` (scale to zero) |
| **Max Workers** | `1` (or higher for prod) |
| **Idle Timeout** | `60` seconds |
| **FlashBoot** | ✅ Enabled |
| **Container Disk** | `20 GB` |
| **Volume** | `30 GB` (for model cache) |
| **Volume Mount** | `/models` |

#### Hunyuan Part Endpoint

| Setting | Value |
|---------|-------|
| **Name** | `modelforge-hunyuan-part` |
| **Docker Image** | `YOUR_DOCKERHUB_USER/hunyuan-part-worker:latest` |
| **GPU Type** | A4000 (16GB) or A5000 (24GB) |
| **Min Workers** | `0` (scale to zero) |
| **Max Workers** | `1` |
| **Idle Timeout** | `60` seconds |
| **FlashBoot** | ✅ Enabled |
| **Container Disk** | `15 GB` |
| **Volume** | `20 GB` (for model cache) |
| **Volume Mount** | `/models` |

3. After creating each endpoint, copy the **Endpoint ID** from the URL:
   `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/...`

## Step 3: Configure ModelForge

Add the endpoint IDs and API key to your `.env`:

```env
# RunPod Serverless
RUNPOD_API_KEY="rpa_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"   # from runpod.io/settings
RUNPOD_ENDPOINT_HUNYUAN_PAINT="abc123def456"               # Endpoint ID from Step 2
RUNPOD_ENDPOINT_HUNYUAN_PART="xyz789ghi012"                # Endpoint ID from Step 2
```

## Step 4: Verify

### Health check via curl

```bash
# Check Paint endpoint health
curl -s https://api.runpod.ai/v2/YOUR_PAINT_ENDPOINT_ID/health \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" | jq .

# Check Part endpoint health
curl -s https://api.runpod.ai/v2/YOUR_PART_ENDPOINT_ID/health \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" | jq .
```

### Test a generation via curl

```bash
# Submit a Paint job
curl -X POST https://api.runpod.ai/v2/YOUR_PAINT_ENDPOINT_ID/run \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "mesh_url": "https://example.com/your-mesh.glb",
      "prompt": "realistic wood texture with grain detail",
      "texture_resolution": "2K",
      "output_format": "glb"
    }
  }'

# Response: {"id": "job-xxx", "status": "IN_QUEUE"}

# Poll status
curl -s https://api.runpod.ai/v2/YOUR_PAINT_ENDPOINT_ID/status/JOB_ID \
  -H "Authorization: Bearer YOUR_RUNPOD_API_KEY" | jq .
```

## Cost Estimates

| Model | GPU | Cost/sec | Typical Job | Est. Cost |
|-------|-----|----------|-------------|-----------|
| Paint | A5000 | ~$0.0002/s | 30-180s | $0.006 – $0.036 |
| Part | A4000 | ~$0.0001/s | 15-60s | $0.002 – $0.006 |

With min workers = 0, you pay **$0 when idle**.

## Troubleshooting

### Cold start taking too long
- Enable **FlashBoot** on the endpoint (caches Docker layers)
- Set min workers to `1` if latency matters more than cost

### Model weight download fails during build
- Ensure `HF_TOKEN` is set if the model repo requires auth
- Add `ENV HF_TOKEN=your-token` to the Dockerfile before the download step

### Out of VRAM
- Paint needs ~21GB → use A5000 (24GB) minimum
- Part needs ~10GB → use A4000 (16GB) minimum
- Never use T4 (16GB) for Paint — it won't fit

### Job times out
- Default timeout is 300s (5 min), configurable in `runpod-client.ts`
- For high-res textures (4K), increase to 600s
