# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# By default, do nothing here—each service overrides command
ENTRYPOINT []
CMD []
