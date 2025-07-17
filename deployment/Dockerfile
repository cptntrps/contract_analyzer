FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY config/requirements.txt ./config/
RUN pip install --no-cache-dir -r config/requirements.txt

# Copy application files
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY templates/ ./templates/
COPY static/ ./static/
COPY config/ ./config/

# Create necessary directories with proper structure
RUN mkdir -p \
    data/uploads \
    data/templates \
    data/reports \
    output/logs \
    output/test-results \
    output/coverage \
    output/artifacts

# Create .env.example if it doesn't exist (for reference)
COPY config/.env.example ./config/.env.example

# Set environment variables for production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8080
ENV FLASK_ENV=production
ENV DEBUG=false
ENV LOG_LEVEL=INFO

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "scripts/start_dashboard.py"]