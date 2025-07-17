FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p uploads contract_templates reports

# Set environment variables
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8080
ENV FLASK_ENV=production
ENV DEBUG=false

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "start_dashboard.py"]