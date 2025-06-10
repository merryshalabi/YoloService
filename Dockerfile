FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy requirements and install dependencies
COPY torch-requirements.txt .
RUN pip install --no-cache-dir -r torch-requirements.txt

# Copy the application code
COPY . .

# Expose the port your Yolo service runs on (usually 8081)
EXPOSE 8081

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "4"]