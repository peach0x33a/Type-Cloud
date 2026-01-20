FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all server code
COPY . .

# Set environment variables
ENV JWT_SECRET=default-secret
ENV PASSWORD=123456
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 3000

# Run the application
CMD ["python", "app.py"]
