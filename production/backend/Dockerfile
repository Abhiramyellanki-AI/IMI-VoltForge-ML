# production/backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install build essentials for compiling certain ML dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file (Ensure you generate this via pip freeze first)
COPY production/backend/requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project context (config.py is in the root)
COPY . /app

# Expose the FastAPI default port
EXPOSE 8000

# Run Uvicorn pointing to the backend main app
CMD ["uvicorn", "production.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
