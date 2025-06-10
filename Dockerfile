FROM python:3.10-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy and install core dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install heavy torch dependencies separately (optional split for caching)
COPY torch-requirements.txt .
RUN pip install --no-cache-dir -r torch-requirements.txt

# Copy the rest of the app code
COPY . .

# Expose the port used by the YOLO FastAPI app
EXPOSE 8081

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "4"]
