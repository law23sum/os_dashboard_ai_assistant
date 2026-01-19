# AI OS Dockerfile
FROM python:3.11-slim

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Add metadata labels
LABEL maintainer="AI OS Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="AI OS" \
      org.label-schema.description="AI-powered desktop application for task management and document processing" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # GUI dependencies (for tkinter)
    tk-dev \
    # Image processing dependencies
    libjpeg-dev \
    libpng-dev \
    # PDF processing dependencies
    libpoppler-cpp-dev \
    poppler-utils \
    # OCR dependencies
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    # Document processing
    antiword \
    unrtf \
    catdoc \
    # Git and version control
    git \
    # Database clients
    postgresql-client \
    redis-tools \
    # Build tools
    build-essential \
    pkg-config \
    # System utilities
    curl \
    wget \
    grep \
    gawk \
    sed \
    jq \
    zip \
    unzip \
    # Additional libraries
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libgomp1 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r osdashboard && \
    useradd -r -g osdashboard -d /app -s /bin/bash osdashboard

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p \
    /app/data \
    /app/logs \
    /app/config \
    /app/file_cache \
    /app/workflows \
    && chown -R osdashboard:osdashboard /app

# Install the application in development mode (for easier debugging)
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER osdashboard

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port for optional web services
EXPOSE 8000

# Default command - run FastAPI server for web deployment
# Override with CMD in docker-compose or ECS task definition if needed
CMD ["gunicorn", "ai_os.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
