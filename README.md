
# QR Code Music Player

This project uses a camera to read QR codes and play the corresponding music file.

## Requirements

* Docker

## Setup

1. **Build the Docker image:**

   ```bash
   docker build \
  --build-arg VIDEO_GID=$(getent group video | cut -d: -f3) \
  --build-arg AUDIO_GID=$(getent group audio | cut -d: -f3) \
  -t qr-player .
   ```

   ```bash
   docker buildexport VIDEO_GID=$(getent group video | cut -d: -f3)
      export AUDIO_GID=$(getent group audio | cut -d: -f3)
      docker compose build
   ```

2. **Run the Docker container:**

   You need to grant the container access to your camera and audio devices. The device path for the camera is usually `/dev/video0`, and for the audio device is usually `/dev/snd`.

   ```bash
      docker run -it --rm \
      --device=/dev/video0 \
      --device=/dev/snd \
      -v ~/Music:/home/appuser/Music \
      qr-player
   ```

   ```bash
   docker compose up
   ```

## Usage

1. Create a QR code that contains the filename of a music file (e.g., `test.mp3`).
2. Place the music file in the `music` directory.
3. Show the QR code to the camera.

The script will play the music file in a loop. If the same QR code is scanned twice, it will be ignored.

## ARM Compatibility

The Docker image is built with ARM compatibility, so it can be deployed on a Raspberry Pi.
