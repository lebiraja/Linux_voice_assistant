FROM python:3.11-slim

# Install system dependencies in smaller chunks to avoid OOM
# First batch: Essential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Second batch: Audio and multimedia libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    python3-tk \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs temp

# Download Whisper model (tiny) during build
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8')"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native

# Run the application
CMD ["python", "main.py"]
