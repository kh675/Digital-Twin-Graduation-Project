FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY dashboard_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r dashboard_requirements.txt

# Copy application files
COPY api/ ./api/
COPY models/ ./models/
COPY roadmaps/ ./roadmaps/
COPY recommendations/ ./recommendations/
COPY skill_gap_profiles/ ./skill_gap_profiles/

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
