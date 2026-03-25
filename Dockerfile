FROM python:3.10-slim

WORKDIR /app

# Install system deps (for OpenCV / InsightFace)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 PRODUCTION SERVER (IMPORTANT)
CMD ["gunicorn", "app:app", "--workers", "1", "--threads", "2", "--timeout", "180", "--bind", "0.0.0.0:10000"]