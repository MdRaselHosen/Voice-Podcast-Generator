# # Base image with Python 3.11
# FROM python:3.11-slim

# # Prevent Python from writing .pyc files and enable stdout/stderr flushing
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# WORKDIR /app

# # Install build dependencies needed for Python packages
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libffi-dev \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# # Copy dependency list first for better caching
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application sources
# COPY . ./

# COPY blog_summary.py ./

# # Use environment variables at runtime for credentials
# # Example: docker run --rm -e FIRECRAWL_API_KEY=... -e HF_TOKEN=... podcast-generator
# CMD ["python", "blog_summary.py"]

# Use Python 3.11 slim image
FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better Docker caching)
COPY requirements.txt .

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .
COPY blog_summary.py .
COPY app.py .

# Dockerfile snippet

# Expose Streamlit's default port
EXPOSE 8501

# Run streamlit directly with network flags enabled
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
