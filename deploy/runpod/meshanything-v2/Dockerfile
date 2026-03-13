# ─────────────────────────────────────────────────────────────────
#  MeshAnything V2 Auto-Retopology — RunPod Serverless Worker
#
#  GPU: A10G (24GB)
#  VRAM: ~12GB during inference
#  Cold start: ~30s with pre-cached weights
#
#  Model: buaacyw/MeshAnythingV2 (Apache 2.0, ICCV 2025)
#  HuggingFace: https://huggingface.co/Yiwen-ntu/meshanythingv2
# ─────────────────────────────────────────────────────────────────

FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/models/meshanythingv2

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

# MeshAnything V2 dependencies (from requirements.txt)
RUN pip install --no-cache-dir \
    trimesh==4.2.3 \
    accelerate==0.28.0 \
    mesh2sdf==1.1.0 \
    einops==0.7.0 \
    einx==0.1.3 \
    optimum==1.18.0 \
    omegaconf==2.3.0 \
    opencv-python==4.9.0.80 \
    transformers==4.39.3 \
    numpy==1.26.4 \
    huggingface_hub \
    safetensors \
    requests

# Clone MeshAnything V2 repo
RUN git clone --depth 1 https://github.com/buaacyw/MeshAnythingV2.git /app/meshanything

# Download model weights (cached in Docker layer)
RUN mkdir -p ${MODEL_DIR} && \
    python -c " \
    from huggingface_hub import snapshot_download; \
    snapshot_download( \
    'Yiwen-ntu/meshanythingv2', \
    local_dir='${MODEL_DIR}', \
    )" || echo "Model download deferred to runtime"

WORKDIR /app

# Copy handler
COPY handler.py /app/handler.py

EXPOSE 8080

CMD ["python", "-u", "/app/handler.py"]
