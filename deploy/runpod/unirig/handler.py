"""
RunPod Serverless Handler — UniRig Auto-Rigging (SIGGRAPH 2025)

Takes a 3D mesh (GLB/OBJ/FBX URL) and generates a fully rigged model
with skeleton and skinning weights using UniRig's autoregressive transformer.

Input:
  {
    "mesh_url": "https://...",             # URL to GLB/OBJ/FBX mesh
    "skeleton_seed": 0,                    # optional: seed for skeleton variation
    "skip_skinning": false                 # optional: return skeleton only (faster)
  }

Output:
  {
    "model_url": "https://...",            # presigned URL to rigged GLB
    "bone_count": 42,                      # number of bones in skeleton
    "execution_time": 12.5                 # seconds
  }

Requirements:
  - GPU: A10G (24GB) or A5000 (24GB) — model needs ~8GB VRAM
  - Docker base: NVIDIA CUDA 12.1 + PyTorch 2.3.1 + Python 3.11

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
# Add UniRig to Python path
# ---------------------------------------------------------------------------

UNIRIG_DIR = Path("/app/unirig")
sys.path.insert(0, str(UNIRIG_DIR))

MODEL_DIR = os.environ.get("MODEL_DIR", "/models/unirig")
WORK_DIR = Path(tempfile.mkdtemp(prefix="unirig_"))

# ---------------------------------------------------------------------------
# File I/O utilities
# ---------------------------------------------------------------------------

def download_file(url: str, suffix: str = ".glb") -> Path:
    """Download a file from URL to a temp path."""
    local_path = WORK_DIR / f"input_{uuid.uuid4().hex[:8]}{suffix}"
    print(f"[UniRig] Downloading {url[:80]}...")
    resp = requests.get(url, timeout=300)
    resp.raise_for_status()
    local_path.write_bytes(resp.content)
    print(f"[UniRig] Downloaded {len(resp.content)} bytes -> {local_path}")
    return local_path


def upload_to_runpod(local_path: Path) -> str:
    """Upload result file and return a presigned URL."""
    try:
        import runpod.serverless.utils.rp_upload as rp_upload
        url = rp_upload.upload_file_to_bucket(str(local_path))
        print(f"[UniRig] Uploaded to RunPod storage: {url[:80]}")
        return url
    except Exception as e:
        print(f"[UniRig] RunPod upload failed ({e}), using base64 fallback")
        import base64
        data = local_path.read_bytes()
        return f"data:application/octet-stream;base64,{base64.b64encode(data).decode()}"


def detect_format(url: str) -> str:
    """Detect input file format from URL."""
    lower = url.lower().split("?")[0]
    for ext in [".obj", ".fbx", ".vrm", ".glb", ".gltf"]:
        if lower.endswith(ext):
            return ext
    return ".glb"


# ---------------------------------------------------------------------------
# UniRig inference via CLI (uses the repo's bash launch scripts)
# ---------------------------------------------------------------------------

def run_unirig_pipeline(
    mesh_path: Path,
    output_dir: Path,
    seed: int = 0,
    skip_skinning: bool = False,
) -> Path:
    """
    Run the full UniRig pipeline:
    1. Skeleton prediction
    2. Skinning weight prediction (optional)
    3. Merge results with original mesh
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    skeleton_out = output_dir / "skeleton.fbx"
    skin_out = output_dir / "skin.fbx"
    final_out = output_dir / "rigged.glb"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(UNIRIG_DIR)

    # Step 1: Skeleton prediction
    print(f"[UniRig] Step 1/3: Predicting skeleton (seed={seed})...")
    skeleton_cmd = [
        "bash", str(UNIRIG_DIR / "launch/inference/generate_skeleton.sh"),
        "--input", str(mesh_path),
        "--output", str(skeleton_out),
        "--seed", str(seed),
    ]
    result = subprocess.run(
        skeleton_cmd, cwd=str(UNIRIG_DIR), env=env,
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Skeleton prediction failed: {result.stderr[-500:]}")
    print(f"[UniRig] Skeleton generated: {skeleton_out}")

    if skip_skinning:
        # Merge skeleton only (no skinning weights)
        print("[UniRig] Step 2/3: Skipping skinning (skip_skinning=True)")
        merge_source = skeleton_out
    else:
        # Step 2: Skinning weight prediction
        print("[UniRig] Step 2/3: Predicting skinning weights...")
        skin_cmd = [
            "bash", str(UNIRIG_DIR / "launch/inference/generate_skin.sh"),
            "--input", str(skeleton_out),
            "--output", str(skin_out),
        ]
        result = subprocess.run(
            skin_cmd, cwd=str(UNIRIG_DIR), env=env,
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Skinning prediction failed: {result.stderr[-500:]}")
        print(f"[UniRig] Skinning weights generated: {skin_out}")
        merge_source = skin_out

    # Step 3: Merge with original mesh
    print("[UniRig] Step 3/3: Merging with original mesh...")
    merge_cmd = [
        "bash", str(UNIRIG_DIR / "launch/inference/merge.sh"),
        "--source", str(merge_source),
        "--target", str(mesh_path),
        "--output", str(final_out),
    ]
    result = subprocess.run(
        merge_cmd, cwd=str(UNIRIG_DIR), env=env,
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Merge failed: {result.stderr[-500:]}")
    print(f"[UniRig] Final rigged model: {final_out}")

    return final_out


def count_bones(glb_path: Path) -> int:
    """Count bones in a GLB file using trimesh."""
    try:
        import trimesh
        scene = trimesh.load(str(glb_path))
        # Approximate bone count from the scene graph
        if hasattr(scene, "graph") and hasattr(scene.graph, "nodes"):
            return len(scene.graph.nodes())
        return -1
    except Exception:
        return -1


# ---------------------------------------------------------------------------
# Job handler
# ---------------------------------------------------------------------------

def handler(job: dict) -> dict:
    """RunPod Serverless handler function."""
    job_input = job.get("input", {})

    mesh_url = job_input.get("mesh_url")
    seed = job_input.get("skeleton_seed", 0)
    skip_skinning = job_input.get("skip_skinning", False)

    if not mesh_url:
        return {"error": "mesh_url is required — provide a URL to GLB/OBJ/FBX mesh"}

    try:
        start = time.time()

        # 1. Download input mesh
        ext = detect_format(mesh_url)
        mesh_path = download_file(mesh_url, suffix=ext)

        # 2. Create output directory for this job
        job_dir = WORK_DIR / f"job_{uuid.uuid4().hex[:8]}"

        # 3. Run UniRig pipeline
        rigged_path = run_unirig_pipeline(
            mesh_path=mesh_path,
            output_dir=job_dir,
            seed=seed,
            skip_skinning=skip_skinning,
        )

        if not rigged_path.exists():
            return {"error": f"Pipeline completed but output not found at {rigged_path}"}

        # 4. Upload result
        model_url = upload_to_runpod(rigged_path)
        elapsed = time.time() - start

        response = {
            "model_url": model_url,
            "bone_count": count_bones(rigged_path),
            "execution_time": round(elapsed, 2),
        }
        return response

    except Exception as e:
        print(f"[UniRig] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        # Cleanup job files
        import shutil
        for d in WORK_DIR.glob("job_*"):
            shutil.rmtree(d, ignore_errors=True)
        for f in WORK_DIR.glob("input_*"):
            f.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[UniRig] Starting UniRig Auto-Rigging RunPod worker...")
    print(f"[UniRig] Model dir: {MODEL_DIR}")
    print(f"[UniRig] Work dir: {WORK_DIR}")
    runpod.serverless.start({"handler": handler})
