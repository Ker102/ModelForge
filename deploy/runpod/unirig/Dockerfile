# ─────────────────────────────────────────────────────────────────
#  UniRig Auto-Rigging — RunPod Serverless Worker
#
#  GPU: A10G (24GB) or A5000 (24GB)
#  VRAM: ~8GB during inference  (16GB recommended for safety)
#  Cold start: ~45s with pre-cached weights
#
#  Model: VAST-AI-Research/UniRig (MIT License, SIGGRAPH 2025)
#  HuggingFace: https://huggingface.co/VAST-AI/UniRig
# ─────────────────────────────────────────────────────────────────

FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/models/unirig
ENV CUDA_HOME=/usr/local/cuda

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-dev python3.11-venv python3-pip \
    git wget curl \
    libgl1-mesa-glx libglib2.0-0 libgomp1 \
    libxi6 libxxf86vm1 libxrender1 libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    python -m pip install --upgrade pip

# PyTorch 2.3 + CUDA 12.1
RUN pip install --no-cache-dir \
    torch==2.3.1 torchvision==0.18.1 \
    --index-url https://download.pytorch.org/whl/cu121

# RunPod SDK
RUN pip install --no-cache-dir runpod==1.7.0

# UniRig Python dependencies (from requirements.txt)
RUN pip install --no-cache-dir \
    transformers==4.51.3 \
    python-box \
    einops \
    omegaconf \
    pytorch_lightning \
    lightning \
    addict \
    timm \
    fast-simplification \
    bpy==4.2 \
    trimesh \
    open3d \
    huggingface_hub \
    numpy==1.26.4

# Flash Attention 2 (requires CUDA dev headers — hence devel base image)
RUN pip install --no-cache-dir flash_attn --no-build-isolation

# spconv for CUDA 12.1
RUN pip install --no-cache-dir spconv-cu121

# torch_scatter and torch_cluster for PyTorch 2.3 + CUDA 12.1
RUN pip install --no-cache-dir \
    torch_scatter torch_cluster \
    -f https://data.pyg.org/whl/torch-2.3.1+cu121.html

# Clone UniRig repo
RUN git clone --depth 1 https://github.com/VAST-AI-Research/UniRig.git /app/unirig

# Download model checkpoints (cached in Docker layer)
RUN mkdir -p ${MODEL_DIR} && \
    python -c " \
    from huggingface_hub import snapshot_download; \
    snapshot_download( \
    'VAST-AI/UniRig', \
    local_dir='${MODEL_DIR}', \
    )" || echo "Model download deferred to runtime"

WORKDIR /app

# Copy handler
COPY handler.py /app/handler.py

EXPOSE 8080

CMD ["python", "-u", "/app/handler.py"]
