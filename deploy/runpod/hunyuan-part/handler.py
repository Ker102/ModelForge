"""
RunPod Serverless Handler — Hunyuan3D Part (Mesh Segmentation)

Takes an input mesh (GLB/OBJ URL) and segments it into semantic parts.
Returns the segmented mesh with labeled parts as a presigned URL.

Input:
  {
    "mesh_url": "https://...",
    "output_format": "glb"        # "glb" | "obj"
  }

Output:
  {
    "model_url": "https://...",    # presigned URL to segmented mesh
    "parts": ["body", "head", ...]  # list of detected segment names
  }

Requirements:
  - GPU: A4000 (16GB) or A5000 (24GB) — model needs ~10GB VRAM
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
MODEL_DIR = os.environ.get("MODEL_DIR", "/models/hunyuan3d-part")


def load_model():
    """Load Hunyuan3D Part segmentation model into GPU memory."""
    global MODEL
    if MODEL is not None:
        return MODEL

    print("[Part] Loading Hunyuan3D Part model...")

    try:
        from hy3dgen.shapegen import Hunyuan3DPartPipeline

        MODEL = Hunyuan3DPartPipeline.from_pretrained(
            MODEL_DIR,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        print("[Part] Model loaded successfully")
    except ImportError:
        # Fallback: try Gradio client approach
        print("[Part] hy3dgen not found, loading via Gradio space as fallback...")
        from gradio_client import Client

        MODEL = Client("tencent/Hunyuan3D-2", verbose=False)
        print("[Part] Loaded via Gradio client")

    return MODEL


# ---------------------------------------------------------------------------
# File I/O utilities
# ---------------------------------------------------------------------------

WORK_DIR = Path(tempfile.mkdtemp(prefix="part_"))


def download_file(url: str, suffix: str = ".glb") -> Path:
    """Download a file from URL to a temp path."""
    local_path = WORK_DIR / f"input_{uuid.uuid4().hex[:8]}{suffix}"
    print(f"[Part] Downloading {url[:80]}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    local_path.write_bytes(resp.content)
    print(f"[Part] Downloaded {len(resp.content)} bytes -> {local_path}")
    return local_path


def upload_to_runpod(local_path: Path) -> str:
    """
    Upload a result file and return a presigned URL.
    Uses RunPod's built-in blob storage via rp_upload.
    """
    try:
        import runpod.serverless.utils.rp_upload as rp_upload

        url = rp_upload.upload_file_to_bucket(str(local_path))
        print(f"[Part] Uploaded to RunPod storage: {url[:80]}")
        return url
    except Exception as e:
        print(f"[Part] RunPod upload failed ({e}), using base64 fallback")
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
    output_format = job_input.get("output_format", "glb")

    if not mesh_url:
        return {"error": "mesh_url is required"}

    try:
        # 1. Load model (cached after first call)
        model = load_model()

        # 2. Download input mesh
        mesh_ext = ".obj" if mesh_url.endswith(".obj") else ".glb"
        mesh_path = download_file(mesh_url, suffix=mesh_ext)

        # 3. Run segmentation
        print(f"[Part] Segmenting mesh from {mesh_path}...")
        output_path = WORK_DIR / f"output_{uuid.uuid4().hex[:8]}.{output_format}"

        # Handle both direct pipeline and Gradio client
        if hasattr(model, "__call__"):
            # Direct pipeline
            result = model(
                mesh_path=str(mesh_path),
                output_path=str(output_path),
            )

            # Parse segment labels from result
            parts = []
            if isinstance(result, dict):
                parts = result.get("parts", [])
                if "output_path" in result:
                    output_path = Path(result["output_path"])
            elif isinstance(result, str) and os.path.exists(result):
                output_path = Path(result)

        elif hasattr(model, "predict"):
            # Gradio client fallback
            result = model.predict(
                str(mesh_path),
                api_name="/segment_mesh",
            )

            parts = []
            if isinstance(result, (list, tuple)) and len(result) > 0:
                output_file = result[0]
                if isinstance(output_file, str) and os.path.exists(output_file):
                    import shutil
                    shutil.copy2(output_file, output_path)
                if len(result) > 1:
                    parts = result[1] if isinstance(result[1], list) else []
        else:
            return {"error": "Model loaded but has no callable interface"}

        if not output_path.exists():
            return {"error": f"Segmentation ran but output file not found at {output_path}"}

        # 4. Upload result
        model_url = upload_to_runpod(output_path)

        return {
            "model_url": model_url,
            "parts": parts,
        }

    except Exception as e:
        print(f"[Part] Error: {e}")
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
    print("[Part] Starting Hunyuan3D Part RunPod worker...")
    # Pre-load model during container startup (before first request)
    load_model()
    runpod.serverless.start({"handler": handler})
