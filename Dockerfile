# Railway-optimized Dockerfile for AI News Analyst
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/vector_db
RUN mkdir -p /app/storage/databases/chroma_db
RUN mkdir -p /app/storage/logs
RUN mkdir -p /app/storage/cache

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Health check (use PORT environment variable)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8002}/health || exit 1

# Start the backend service (which now serves both API and frontend)
CMD ["python", "scripts/start_production.py"]
