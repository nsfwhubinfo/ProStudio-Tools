# Multi-stage Dockerfile for ProStudio Dynamic Memory Caching
# ===========================================================
# Optimized for minimal size and zero-cost deployment

# Stage 1: Build environment
FROM python:3.9-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user \
    gunicorn \
    gevent \
    redis \
    cython \
    numpy \
    scipy \
    scikit-learn \
    flask \
    flask-cors \
    psutil

# Copy source code
COPY core/ ./core/
COPY *.py ./

# Compile Cython extensions if present
RUN cd core/acceleration && \
    python setup.py build_ext --inplace || true

# Stage 2: Runtime environment
FROM python:3.9-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash prostudio

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/prostudio/.local

# Copy application code from builder
COPY --from=builder /build/ ./

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/tmp && \
    chown -R prostudio:prostudio /app

# Copy startup script
COPY deploy/zero-cost/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Switch to non-root user
USER prostudio

# Update PATH
ENV PATH=/home/prostudio/.local/bin:$PATH

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["/app/start.sh"]