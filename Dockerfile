# Use official Python slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Set environment to production (optional)
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "ai-alert.py"]

