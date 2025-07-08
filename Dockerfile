FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/input /app/data/output /app/data/upload /app/runs/detect/pallet_model2/weights

# Copy pre-trained model (adjust path if model is included in repo)
COPY runs/detect/pallet_model2/weights/best.pt /app/runs/detect/pallet_model2/weights/best.pt

# Set environment variables
ENV FLASK_APP=src/api/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Command to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.api.app:app"]
