"""
RunPod Serverless Handler — Hunyuan3D Paint 2.1 (PBR Texturing)

Takes an input mesh (GLB/OBJ URL) and generates PBR textures using
Hunyuan3D Paint 2.1. Returns the textured mesh as a presigned URL.

Input:
  {
    "mesh_url": "https://...",
    "prompt": "high quality PBR texture",
    "texture_resolution": "2K",   # "1K" | "2K" | "4K"
    "output_format": "glb"        # "glb" | "obj"
  }

Output:
  {
    "model_url": "https://...",    # presigned URL to textured GLB
    "texture_url": "https://..."   # optional separate texture map
  }

Requirements:
  - GPU: A5000 (24GB) or A100 (40/80GB) — model needs ~21GB VRAM
  - Docker base: NVIDIA CUDA 12.1 + PyTorch 2.2

RunPod Serverless docs: https://docs.runpod.io/serverless/workers/handler-functions
"""

import os
import runpod
import torch
import requests
import tempfile
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Model loading (called once at container startup, cached in memory)
# ---------------------------------------------------------------------------

MODEL = None
MODEL_DIR = os.environ.get("MODEL_DIR", "/models/hunyuan3d-paint")


def load_model():
    """Load Hunyuan3D Paint 2.1 model weights into GPU memory."""
    global MODEL
    if MODEL is not None:
        return MODEL

    print("[Paint] Loading Hunyuan3D Paint 2.1 model...")

    try:
        from hy3dgen.texgen import Hunyuan3DPaintPipeline

        MODEL = Hunyuan3DPaintPipeline.from_pretrained(
            MODEL_DIR,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        print("[Paint] Model loaded successfully")
    except ImportError:
        # Fallback: try loading from transformers/diffusers pattern
        print("[Paint] hy3dgen not found, attempting diffusers-based loading...")
        from diffusers import StableDiffusionPipeline

        MODEL = StableDiffusionPipeline.from_pretrained(
            MODEL_DIR,
            torch_dtype=torch.float16,
        ).to("cuda")
        print("[Paint] Model loaded via diffusers fallback")

    return MODEL


# ---------------------------------------------------------------------------
# File I/O utilities
# ---------------------------------------------------------------------------

WORK_DIR = Path(tempfile.mkdtemp(prefix="paint_"))


def download_file(url: str, suffix: str = ".glb") -> Path:
    """Download a file from URL to a temp path."""
    local_path = WORK_DIR / f"input_{uuid.uuid4().hex[:8]}{suffix}"
    print(f"[Paint] Downloading {url[:80]}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    local_path.write_bytes(resp.content)
    print(f"[Paint] Downloaded {len(resp.content)} bytes -> {local_path}")
    return local_path


def upload_to_runpod(local_path: Path) -> str:
    """
    Upload a result file and return a presigned URL.
    Uses RunPod's built-in blob storage via rp_upload.
    """
    try:
        import runpod.serverless.utils.rp_upload as rp_upload

        url = rp_upload.upload_file_to_bucket(str(local_path))
        print(f"[Paint] Uploaded to RunPod storage: {url[:80]}")
        return url
    except Exception as e:
        print(f"[Paint] RunPod upload failed ({e}), using base64 fallback")
        import base64

        data = local_path.read_bytes()
        return f"data:application/octet-stream;base64,{base64.b64encode(data).decode()}"


# ---------------------------------------------------------------------------
# Job handler
# ---------------------------------------------------------------------------

def handler(job: dict) -> dict:
    """
    RunPod Serverless handler function.
    Called for each incoming job. Must return a dict.
    """
    job_input = job.get("input", {})

    mesh_url = job_input.get("mesh_url")
    prompt = job_input.get("prompt", "high quality PBR texture")
    texture_resolution = job_input.get("texture_resolution", "2K")
    output_format = job_input.get("output_format", "glb")

    if not mesh_url:
        return {"error": "mesh_url is required"}

    try:
        # 1. Load model (cached after first call)
        model = load_model()

        # 2. Download input mesh
        mesh_ext = ".obj" if mesh_url.endswith(".obj") else ".glb"
        mesh_path = download_file(mesh_url, suffix=mesh_ext)

        # 3. Generate PBR textures
        print(f"[Paint] Generating textures: prompt='{prompt}', resolution={texture_resolution}")

        # Resolution mapping
        res_map = {"1K": 1024, "2K": 2048, "4K": 4096}
        resolution = res_map.get(texture_resolution, 2048)

        output_path = WORK_DIR / f"output_{uuid.uuid4().hex[:8]}.{output_format}"

        # Run the texturing pipeline
        result = model(
            mesh_path=str(mesh_path),
            prompt=prompt,
            resolution=resolution,
            output_path=str(output_path),
        )

        # Handle different return types from the pipeline
        if isinstance(result, str) and os.path.exists(result):
            output_path = Path(result)
        elif isinstance(result, dict) and "output_path" in result:
            output_path = Path(result["output_path"])

        if not output_path.exists():
            return {"error": f"Pipeline ran but output file not found at {output_path}"}

        # 4. Upload result
        model_url = upload_to_runpod(output_path)

        response = {"model_url": model_url}

        # Check for separate texture files
        texture_path = output_path.with_suffix(".png")
        if texture_path.exists():
            response["texture_url"] = upload_to_runpod(texture_path)

        return response

    except Exception as e:
        print(f"[Paint] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        # Clean up temp files for this job
        for f in WORK_DIR.glob("input_*"):
            f.unlink(missing_ok=True)
        for f in WORK_DIR.glob("output_*"):
            f.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[Paint] Starting Hunyuan3D Paint 2.1 RunPod worker...")
    # Pre-load model during container startup (before first request)
    load_model()
    runpod.serverless.start({"handler": handler})
