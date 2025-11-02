# Use a multi-stage build to keep the final image small
FROM python:3.10-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libzbar0 \
    libzbar-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.10-slim-bookworm

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libasound2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    vlc v4l-utils ffmpeg alsa-utils \
    libsm6 libxext6 libxrender-dev libgl1

# --- Create non-root user with host-matched video/audio GIDs ---
ARG VIDEO_GID=985
ARG AUDIO_GID=996
RUN groupmod -g ${VIDEO_GID} video || groupadd -g ${VIDEO_GID} video; \
    groupmod -g ${AUDIO_GID} audio || groupadd -g ${AUDIO_GID} audio; \
    useradd --create-home --shell /bin/bash -u 1000 -G video,audio appuser
WORKDIR /home/appuser
USER appuser

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the application code
COPY src/ .
COPY music/ ./music/

# Command to run the application
CMD ["python", "main.py"]
