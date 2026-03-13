"""
RunPod Serverless Handler — MoMask Text-to-Motion (CVPR 2024)

Generates realistic human motion (BVH) from text descriptions using
MoMask's masked generative transformer architecture.

Input:
  {
    "prompt": "A person walks forward and waves hello",
    "duration": 4.0,           # optional: motion duration in seconds (default 4.0)
    "format": "bvh",           # optional: "bvh" (default)
    "seed": 0,                 # optional: random seed
    "repeat": 1                # optional: number of variations
  }

Output:
  {
    "motion_url": "https://...",   # presigned URL to BVH file
    "duration": 4.0,               # actual duration in seconds
    "frame_count": 80,             # number of frames (20 fps)
    "execution_time": 3.2          # seconds
  }

Requirements:
  - GPU: A10G (24GB) — also works on CPU but slower
  - VRAM: ~8GB
  - Docker base: NVIDIA CUDA 12.1 + PyTorch 2.2

RunPod Serverless docs: https://docs.runpod.io/serverless/workers/handler-functions
"""

import os
import sys
import runpod
import requests
import tempfile
import uuid
import time
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MOMASK_DIR = Path("/app/momask")
sys.path.insert(0, str(MOMASK_DIR))

WORK_DIR = Path(tempfile.mkdtemp(prefix="momask_"))
FPS = 20  # MoMask generates at 20 fps


# ---------------------------------------------------------------------------
# File I/O utilities
# ---------------------------------------------------------------------------

def upload_to_runpod(local_path: Path) -> str:
    """Upload result file and return a presigned URL."""
    try:
        import runpod.serverless.utils.rp_upload as rp_upload
        url = rp_upload.upload_file_to_bucket(str(local_path))
        print(f"[MoMask] Uploaded to RunPod storage: {url[:80]}")
        return url
    except Exception as e:
        print(f"[MoMask] RunPod upload failed ({e}), using base64 fallback")
        import base64
        data = local_path.read_bytes()
        return f"data:application/octet-stream;base64,{base64.b64encode(data).decode()}"


# ---------------------------------------------------------------------------
# MoMask inference via CLI
# ---------------------------------------------------------------------------

def generate_motion(
    prompt: str,
    duration: float = 4.0,
    seed: int = 0,
    repeat: int = 1,
) -> dict:
    """
    Run MoMask text-to-motion generation.
    Returns dict with output paths and metadata.
    """
    # Calculate motion_length (number of poses at 20fps, rounded to nearest 4)
    motion_length = max(4, round(duration * FPS / 4) * 4)

    ext_name = f"runpod_{uuid.uuid4().hex[:8]}"
    output_dir = MOMASK_DIR / "generation" / ext_name

    env = os.environ.copy()
    env["PYTHONPATH"] = str(MOMASK_DIR)

    # Use GPU 0
    cmd = [
        "python", str(MOMASK_DIR / "gen_t2m.py"),
        "--gpu_id", "0",
        "--ext", ext_name,
        "--text_prompt", prompt,
        "--motion_length", str(motion_length),
        "--repeat_times", str(repeat),
    ]

    print(f"[MoMask] Generating: prompt='{prompt}', length={motion_length} frames, seed={seed}")
    result = subprocess.run(
        cmd, cwd=str(MOMASK_DIR), env=env,
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"MoMask generation failed: {result.stderr[-500:]}")

    # Find output BVH file
    bvh_dir = output_dir / "animation"
    if not bvh_dir.exists():
        raise RuntimeError(f"Output directory not found: {bvh_dir}")

    bvh_files = list(bvh_dir.glob("*.bvh"))
    if not bvh_files:
        raise RuntimeError(f"No BVH files generated in {bvh_dir}")

    # Prefer the IK-corrected version if available
    ik_files = [f for f in bvh_files if "_ik" in f.name]
    best_bvh = ik_files[0] if ik_files else bvh_files[0]

    print(f"[MoMask] Generated BVH: {best_bvh}")

    return {
        "bvh_path": best_bvh,
        "frame_count": motion_length,
        "duration": motion_length / FPS,
        "output_dir": output_dir,
    }


# ---------------------------------------------------------------------------
# Job handler
# ---------------------------------------------------------------------------

def handler(job: dict) -> dict:
    """RunPod Serverless handler function."""
    job_input = job.get("input", {})

    prompt = job_input.get("prompt")
    duration = job_input.get("duration", 4.0)
    seed = job_input.get("seed", 0)
    repeat = job_input.get("repeat", 1)

    if not prompt:
        return {"error": "prompt is required — describe the human motion you want."}

    try:
        start = time.time()

        # Generate motion
        result = generate_motion(
            prompt=prompt,
            duration=duration,
            seed=seed,
            repeat=repeat,
        )

        # Upload BVH
        motion_url = upload_to_runpod(result["bvh_path"])
        elapsed = time.time() - start

        response = {
            "motion_url": motion_url,
            "duration": result["duration"],
            "frame_count": result["frame_count"],
            "execution_time": round(elapsed, 2),
        }
        return response

    except Exception as e:
        print(f"[MoMask] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        # Cleanup generated files
        import shutil
        for d in (MOMASK_DIR / "generation").glob("runpod_*"):
            shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[MoMask] Starting MoMask Text-to-Motion RunPod worker...")
    runpod.serverless.start({"handler": handler})
