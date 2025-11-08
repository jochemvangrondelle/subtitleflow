FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip install --system -e ".[dev]"

# Copy application code
COPY . .

# Create directories for data, output, and cache
RUN mkdir -p /app/data /app/output /app/cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://ollama:11434

# Default command
CMD ["python", "-m", "subtitleflow", "--help"]

