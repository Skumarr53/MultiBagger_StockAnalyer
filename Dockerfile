Here’s the reformatted Dockerfile content for better readability:

```dockerfile
# Dockerfile for AI Stock Picker (multi-env: CPU default, GPU optional)

# === BASE IMAGE ===
# CPU: slim base; for GPU, see below
FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    git \
    curl \
    wget \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy config and lock files
COPY pyproject.toml requirements.txt ./

# Install Poetry and uv
RUN pip install poetry uv

# ========== CPU (default) ==========
# Install only CPU dependencies
RUN poetry install --no-interaction --no-ansi --extras cpu

# ========== GPU (uncomment to enable) ==========
# FROM nvidia/cuda:12.2.0-base-ubuntu22.04
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     git \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*
# COPY pyproject.toml requirements.txt ./
# RUN pip install poetry uv torch faiss-gpu
# RUN poetry install --no-interaction --no-ansi --extras gpu

# Download spaCy model (en_core_web_sm)
RUN python -m spacy download en_core_web_sm

# Copy the entire codebase
COPY . .

# Expose dashboard port (Streamlit default)
EXPOSE 8501

# Default: run Streamlit dashboard
CMD ["streamlit", "run", "dashboard/app.py"]

# For pipeline run:
# CMD ["python", "orchestrator.py"]
```

This formatting improves readability by organizing the comments and commands clearly, making it easier to understand the structure of the Dockerfile.