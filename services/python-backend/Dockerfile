# services/python-backend/Dockerfile
FROM python:3.12-slim

# Install some basic utilities
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1 \
        && \
    rm -rf /var/lib/apt/lists/*


# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# First, copy the dependency files
COPY pyproject.toml .

# Installing dependencies via uv
RUN uv pip install --system .

# Копируем остальной код
COPY . .
