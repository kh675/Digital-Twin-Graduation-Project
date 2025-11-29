#!/bin/bash
# Start script for API deployment on Render.com or similar platforms

echo "Starting Digital Twin AI API..."

# Set default port if not provided
PORT=${PORT:-8000}

# Start the API with uvicorn
uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 2
