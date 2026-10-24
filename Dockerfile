# OmniGrab - Universal Media Downloader Dockerfile
FROM python:3.11-slim

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install FFmpeg, Node.js, and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure downloads directory exists
RUN mkdir -p downloads

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
