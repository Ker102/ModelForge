# ─────────────────────────────────────────────────────────────────
#  Hunyuan3D Paint 2.1 — RunPod Serverless Worker
#
#  GPU: A5000/A6000 (24GB) or A100 (40/80GB)
#  VRAM: ~21GB during inference
#  Cold start: ~30s with FlashBoot + pre-cached weights
# ─────────────────────────────────────────────────────────────────

FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/models/hunyuan3d-paint

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3-pip python3-dev \
    git wget curl \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3

# PyTorch 2.2 + CUDA 12.1
RUN pip install --no-cache-dir \
    torch==2.2.0 torchvision==0.17.0 \
    --index-url https://download.pytorch.org/whl/cu121

# RunPod SDK
RUN pip install --no-cache-dir runpod==1.7.0

# Hunyuan3D dependencies
RUN pip install --no-cache-dir \
    transformers>=4.40.0 \
    diffusers>=0.27.0 \
    accelerate>=0.28.0 \
    safetensors \
    trimesh \
    pillow \
    numpy \
    requests \
    pygltflib \
    xatlas

# Clone and install Hunyuan3D-2
RUN git clone --depth 1 https://github.com/Tencent/Hunyuan3D-2.git /app/hunyuan3d && \
    cd /app/hunyuan3d && \
    pip install --no-cache-dir -e . 2>/dev/null || true

# Download model weights (cached in Docker layer)
# The paint model is part of the Hunyuan3D-2 release
RUN mkdir -p ${MODEL_DIR} && \
    python -c " \
from huggingface_hub import snapshot_download; \
snapshot_download( \
    'tencent/Hunyuan3D-2', \
    local_dir='${MODEL_DIR}', \
    allow_patterns=['*paint*', 'config*', '*.json', '*.safetensors'], \
    ignore_patterns=['*shape*', '*.bin', '*.ckpt'], \
)" || echo "Model download deferred to runtime"

WORKDIR /app

# Copy handler
COPY handler.py /app/handler.py

# Pre-download any remaining model components
# (this ensures FlashBoot cache includes everything)

EXPOSE 8080

CMD ["python", "-u", "/app/handler.py"]
