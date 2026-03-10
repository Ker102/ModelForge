"""
RunPod Serverless Handler — MeshAnything V2 Auto-Retopology (ICCV 2025)

Takes a high-poly mesh (GLB/OBJ URL) and generates a clean, quad-dominant
retopologized mesh using MeshAnything V2's Adjacent Mesh Tokenization.

Input:
  {
    "mesh_url": "https://...",        # URL to GLB/OBJ mesh
    "target_faces": 800,              # optional: target face count (max 1600)
    "output_format": "glb",           # optional: "glb" | "obj"
    "marching_cubes": false,          # optional: pre-process with marching cubes
    "seed": 0                         # optional: random seed
  }

Output:
  {
    "model_url": "https://...",       # presigned URL to retopologized mesh
    "face_count": 812,                # actual face count of output
    "execution_time": 15.3            # seconds
  }

Requirements:
  - GPU: A10G (24GB) — model needs ~12GB VRAM
  - Docker base: NVIDIA CUDA 12.1 + PyTorch 2.2

RunPod Serverless docs: https://docs.runpod.io/serverless/workers/handler-functions
"""

import os
import sys
import runpod
import torch
import requests
import tempfile
import uuid
import time
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Add MeshAnything to Python path
# ---------------------------------------------------------------------------

MESHANYTHING_DIR = Path("/app/meshanything")
sys.path.insert(0, str(MESHANYTHING_DIR))

MODEL_DIR = os.environ.get("MODEL_DIR", "/models/meshanythingv2")
WORK_DIR = Path(tempfile.mkdtemp(prefix="meshanything_"))
MAX_TARGET_FACES = 1600

# ---------------------------------------------------------------------------
# Model loading (singleton)
# ---------------------------------------------------------------------------

MODEL = None


def load_model():
    """Load MeshAnything V2 model."""
    global MODEL
    if MODEL is not None:
        return MODEL

    print("[MeshAnything] Loading MeshAnything V2 model...")
    from MeshAnything.models.meshanything_v2 import MeshAnythingV2

    MODEL = MeshAnythingV2.from_pretrained("Yiwen-ntu/meshanythingv2")
    MODEL.eval()
    print("[MeshAnything] Model loaded successfully")
    return MODEL


# ---------------------------------------------------------------------------
# File I/O utilities
# ---------------------------------------------------------------------------

def download_file(url: str, suffix: str = ".glb") -> Path:
    """Download a file from URL to a temp path."""
    local_path = WORK_DIR / f"input_{uuid.uuid4().hex[:8]}{suffix}"
    print(f"[MeshAnything] Downloading {url[:80]}...")
    resp = requests.get(url, timeout=300)
    resp.raise_for_status()
    local_path.write_bytes(resp.content)
    print(f"[MeshAnything] Downloaded {len(resp.content)} bytes -> {local_path}")
    return local_path


def upload_to_runpod(local_path: Path) -> str:
    """Upload result file and return a presigned URL."""
    try:
        import runpod.serverless.utils.rp_upload as rp_upload
        url = rp_upload.upload_file_to_bucket(str(local_path))
        print(f"[MeshAnything] Uploaded to RunPod storage: {url[:80]}")
        return url
    except Exception as e:
        print(f"[MeshAnything] RunPod upload failed ({e}), using base64 fallback")
        import base64
        data = local_path.read_bytes()
        return f"data:application/octet-stream;base64,{base64.b64encode(data).decode()}"


# ---------------------------------------------------------------------------
# Retopology inference
# ---------------------------------------------------------------------------

def retopologize(mesh_path: Path, output_path: Path, marching_cubes: bool = False) -> int:
    """
    Run MeshAnything V2 retopology on a single mesh.
    Returns the face count of the output.
    """
    import trimesh
    from accelerate import Accelerator
    from accelerate.utils import DistributedDataParallelKwargs

    # Import the mesh-to-point-cloud conversion
    from mesh_to_pc import process_mesh_to_pc

    model = load_model()

    # Load input mesh
    input_mesh = trimesh.load(str(mesh_path))
    print(f"[MeshAnything] Input mesh: {len(input_mesh.faces)} faces")

    # Convert mesh to point cloud (8192 points with normals)
    pc_list, _ = process_mesh_to_pc([input_mesh], marching_cubes=marching_cubes)
    pc_normal = pc_list[0]  # (8192, 6) — xyz + normals

    # Normalize point cloud coordinates
    pc_coor = pc_normal[:, :3]
    normals = pc_normal[:, 3:]
    bounds = np.array([pc_coor.min(axis=0), pc_coor.max(axis=0)])
    pc_coor = pc_coor - (bounds[0] + bounds[1])[None, :] / 2
    pc_coor = pc_coor / np.abs(pc_coor).max() * 0.9995
    pc_normal = np.concatenate([pc_coor, normals], axis=-1, dtype=np.float16)

    # Run inference
    kwargs = DistributedDataParallelKwargs(find_unused_parameters=True)
    accelerator = Accelerator(
        mixed_precision="fp16",
        kwargs_handlers=[kwargs],
    )
    model = accelerator.prepare(model)

    with accelerator.autocast():
        pc_tensor = torch.from_numpy(pc_normal).unsqueeze(0).to(accelerator.device)
        outputs = model(pc_tensor, sampling=False)

    # Process output
    recon_mesh = outputs[0]
    valid_mask = torch.all(~torch.isnan(recon_mesh.reshape((-1, 9))), dim=1)
    recon_mesh = recon_mesh[valid_mask]

    vertices = recon_mesh.reshape(-1, 3).cpu().numpy()
    vertices_index = np.arange(len(vertices))
    triangles = vertices_index.reshape(-1, 3)

    # Build clean trimesh
    scene_mesh = trimesh.Trimesh(
        vertices=vertices, faces=triangles,
        force="mesh", merge_primitives=True,
    )
    scene_mesh.merge_vertices()
    scene_mesh.update_faces(scene_mesh.nondegenerate_faces())
    scene_mesh.update_faces(scene_mesh.unique_faces())
    scene_mesh.remove_unreferenced_vertices()
    scene_mesh.fix_normals()

    face_count = len(scene_mesh.faces)
    print(f"[MeshAnything] Output mesh: {face_count} faces")

    # Export
    scene_mesh.export(str(output_path))
    return face_count


# ---------------------------------------------------------------------------
# Job handler
# ---------------------------------------------------------------------------

def handler(job: dict) -> dict:
    """RunPod Serverless handler function."""
    job_input = job.get("input", {})

    mesh_url = job_input.get("mesh_url")
    output_format = job_input.get("output_format", "glb")
    marching_cubes = job_input.get("marching_cubes", False)

    if not mesh_url:
        return {"error": "mesh_url is required — provide the mesh to retopologize."}

    try:
        start = time.time()

        # 1. Download input mesh
        ext = ".obj" if mesh_url.lower().split("?")[0].endswith(".obj") else ".glb"
        mesh_path = download_file(mesh_url, suffix=ext)

        # 2. Run retopology
        out_ext = "obj" if output_format == "obj" else "glb"
        output_path = WORK_DIR / f"retopo_{uuid.uuid4().hex[:8]}.{out_ext}"

        face_count = retopologize(
            mesh_path=mesh_path,
            output_path=output_path,
            marching_cubes=marching_cubes,
        )

        if not output_path.exists():
            return {"error": f"Retopology ran but output not found at {output_path}"}

        # 3. Upload result
        model_url = upload_to_runpod(output_path)
        elapsed = time.time() - start

        return {
            "model_url": model_url,
            "face_count": face_count,
            "execution_time": round(elapsed, 2),
        }

    except Exception as e:
        print(f"[MeshAnything] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        # Cleanup
        for f in WORK_DIR.glob("input_*"):
            f.unlink(missing_ok=True)
        for f in WORK_DIR.glob("retopo_*"):
            f.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[MeshAnything] Starting MeshAnything V2 RunPod worker...")
    # Pre-load model during container startup
    load_model()
    runpod.serverless.start({"handler": handler})
