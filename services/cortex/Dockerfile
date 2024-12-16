FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/cortex/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/cortex/ .

# Set environment variables for PyTorch and Metal optimization
ENV PYTHONUNBUFFERED=1 \
    PYTORCH_ENABLE_MPS_FALLBACK=1 \
    METAL_DEVICE_WRAPPER_TYPE=1 \
    PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.7 \
    PYTORCH_MPS_LOW_WATERMARK_RATIO=0.5 \
    PYTHONPATH=/app

# Create cache directory for models
RUN mkdir -p /root/.cache/huggingface && \
    mkdir -p /root/.cache/torch

# Verify PyTorch installation and Metal support
RUN python -c "import torch; print(f'PyTorch version: {torch.__version__}'); \
    print(f'MPS (Metal) available: {torch.backends.mps.is_available()}'); \
    print(f'Using device: {torch.device(\"mps\" if torch.backends.mps.is_available() else \"cpu\")}')"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set the default command
CMD ["python", "-m", "quantum_terminal"]
