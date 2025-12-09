# OS Dashboard AI Assistant Platform - Docker Configuration
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    poppler-utils \
    wkhtmltopdf \
    antiword \
    unrtf \
    catdoc \
    grep \
    gawk \
    sed \
    jq \
    xmlstarlet \
    tmux \
    vim \
    tree \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for web components
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p workspace output logs temp backups

# Set permissions
RUN chmod +x main.py

# Expose ports
EXPOSE 8000 8080 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "main.py", "--mode", "server", "--port", "8000"]

# Alternative commands:
# For GUI mode: docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix os-dashboard-ai python main.py --mode dashboard
# For CLI mode: docker run -it os-dashboard-ai python main.py --mode cli
# For demo: docker run os-dashboard-ai python examples/demo_usage.py