FROM python:3.10-slim

WORKDIR /app

# Install required system libraries for OpenCV and general stability
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install lightweight Python dependencies (FastAPI, boto3, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install heavy torch and ultralytics dependencies
COPY torch-requirements.txt .
RUN pip install --no-cache-dir -r torch-requirements.txt

# Copy the application code
COPY . .

# Create required directories at build-time (optional, for local runs)
RUN mkdir -p uploads/original uploads/predicted

# Expose the FastAPI port
EXPOSE 8081

# Run the FastAPI server with multiple workers
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "4"]
