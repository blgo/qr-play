
# QR Code Music Player

This project uses a camera to read QR codes and play the corresponding music file.

## Requirements

* Docker

## Setup

1. **Build the Docker image:**

   ```bash
   docker build -t qr-player .
   ```

2. **Run the Docker container:**

   You need to grant the container access to your camera and audio devices. The device path for the camera is usually `/dev/video0`, and for the audio device is usually `/dev/snd`.

   ```bash
   docker run -it --rm \                        [130] main?
  --device=/dev/video0 \
  --device=/dev/video1 \
  --device=/dev/snd \
  --group-add audio \
  --group-add video \
  --env DISPLAY=$DISPLAY \
  --env XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
  --env PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \ 
  -v /run/user/$(id -u)/pulse:/run/user/$(id -u)/pulse \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  qr-player
   ```

## Usage

1. Create a QR code that contains the filename of a music file (e.g., `test.mp3`).
2. Place the music file in the `music` directory.
3. Show the QR code to the camera.

The script will play the music file in a loop. If the same QR code is scanned twice, it will be ignored.

## ARM Compatibility

The Docker image is built with ARM compatibility, so it can be deployed on a Raspberry Pi.
