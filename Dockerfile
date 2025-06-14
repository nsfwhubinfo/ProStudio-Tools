# ===================================================================
# Stage 1: Builder - Install dependencies into a virtual environment
# ===================================================================
FROM python:3.9-slim AS builder

# Install system-level build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ===================================================================
# Stage 2: Final - Create the lean, production image
# ===================================================================
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application
RUN useradd -m -u 1000 -s /bin/bash prostudio

# Set the working directory
WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code into the container
COPY . /app/

# Create necessary directories and set ownership
RUN mkdir -p /app/logs /app/cache && \
    chown -R prostudio:prostudio /app
RUN chmod +x /app/start.sh

# Switch to the non-root user
USER prostudio

# Make the venv's Python the default
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Set the default command to run the startup script
CMD ["/app/start.sh"]