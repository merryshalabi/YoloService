FROM python:3.10-slim

# Use environment variable for non-interactive apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install required system libraries in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .
COPY torch-requirements.txt .

# Upgrade pip and install dependencies in one layer
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r torch-requirements.txt

# Copy the rest of the source code (only after deps are installed to leverage cache)
COPY . .

# Run the FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "4"]
