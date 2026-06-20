# Use official Python 3.11 slim image (NOT 3.13 – more stable for cv2)
FROM python:3.11-slim

# Install system libraries required by opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    libx11-6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Force remove GUI opencv if present, install headless only
RUN pip install --upgrade pip && \
    pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null || true && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (Railway injects $PORT at runtime)
EXPOSE 8501

# Run Streamlit
CMD streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true
