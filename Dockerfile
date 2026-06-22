# Base Python Image
FROM python:3.11-slim

# Working Directory inside container
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose FastAPI Port
EXPOSE 8000

# Start Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]