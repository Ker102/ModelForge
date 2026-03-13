# ─────────────────────────────────────────────────────────────────
#  MoMask Text-to-Motion — RunPod Serverless Worker
#
#  GPU: A10G (24GB) or even CPU-only (slower but works)
#  VRAM: ~8GB during inference
#  Cold start: ~20s with pre-cached weights
#
#  Model: EricGuo5513/momask-codes (MIT License, CVPR 2024)
# ─────────────────────────────────────────────────────────────────

FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV MODEL_DIR=/models/momask

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3-pip python3-dev \
    git wget curl \
    ffmpeg \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3

# PyTorch 2.2 + CUDA 12.1 (MoMask works with modern PyTorch despite old requirements)
RUN pip install --no-cache-dir \
    torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 \
    --index-url https://download.pytorch.org/whl/cu121

# RunPod SDK
RUN pip install --no-cache-dir runpod==1.7.0

# MoMask dependencies (modernized from requirements.txt)
RUN pip install --no-cache-dir \
    clip @ git+https://github.com/openai/CLIP.git \
    einops==0.6.1 \
    ftfy \
    gdown \
    matplotlib \
    numpy==1.26.4 \
    Pillow \
    PyYAML \
    scikit-learn \
    scipy \
    smplx==0.1.28 \
    tqdm \
    trimesh \
    vector-quantize-pytorch==1.6.30 \
    requests

# Clone MoMask repo
RUN git clone --depth 1 https://github.com/EricGuo5513/momask-codes.git /app/momask

WORKDIR /app/momask

# Download pre-trained models
RUN bash prepare/download_models.sh || echo "Model download deferred to runtime"

# Download GloVe embeddings (needed for text processing)
RUN bash prepare/download_glove.sh || echo "GloVe download deferred to runtime"

# Copy handler
COPY handler.py /app/handler.py

EXPOSE 8080

CMD ["python", "-u", "/app/handler.py"]
