FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python to unbuffered mode for real-time logs
ENV PYTHONUNBUFFERED=1

# Start the application
CMD ["python", "app.py"]
