# Dockerfile
# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env ./

# Set environment variables
ENV FLASK_APP=src/api/app.py
ENV PYTHONUNBUFFERED=1

# Expose Flask port
EXPOSE 5000

# Start Flask app
CMD ["python", "src/api/app.py"]
