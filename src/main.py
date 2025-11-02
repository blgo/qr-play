
import cv2
from pyzbar import pyzbar
import time
import os
import random
import subprocess
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the camera
logging.debug("Initializing camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Cannot open camera")
    exit()

vlc_process = None

def play_with_vlc(file_path):
    global vlc_process
    logging.debug(f"Attempting to play {file_path} with VLC.")
    # Stop old VLC instance
    if vlc_process and vlc_process.poll() is None:
        logging.debug("Terminating previous VLC process.")
        vlc_process.terminate()
    # Start new VLC in loop
    logging.debug(f"Starting new VLC process for {file_path}.")
    vlc_process = subprocess.Popen(["cvlc", "--loop", file_path])

def stop_vlc():
    global vlc_process
    logging.debug("Stopping VLC playback.")
    if vlc_process and vlc_process.poll() is None:
        vlc_process.terminate()
        vlc_process = None

# Set to store previously scanned QR codes
last_qr_code = ""
last_random_trigger_time = datetime.min

# Directory where music files are stored
music_dir = "music"
logging.debug(f"Music directory set to: {music_dir}")

while True:
    logging.debug("Reading frame from camera.")
    # Read a frame from the camera
    ret, frame = cap.read()

    if ret:
        logging.debug("Frame read successfully.")
        # Decode QR codes
        barcodes = pyzbar.decode(frame)

        # if not barcodes:
            # logging.debug("No QR codes found in frame.")

        for barcode in barcodes:
            # Get the data from the QR code
            qr_data = barcode.data.decode("utf-8")
            logging.debug(f"Decoded QR data: {qr_data}")

            # If the QR code has not been scanned before
            if qr_data != last_qr_code:
                logging.info(f"New QR code detected: {qr_data}")
                last_qr_code = qr_data

                # Save a snapshot
                snapshot_filename = os.path.join(music_dir, f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jpeg")
                logging.debug(f"Saving snapshot to {snapshot_filename}")
                cv2.imwrite(snapshot_filename, frame)


                if qr_data == "random":
                    last_qr_code = ""
                    if datetime.now() - last_random_trigger_time > timedelta(seconds=3):
                        last_random_trigger_time = datetime.now()
                        logging.debug("Random QR code triggered.")
                        # random can be reused
                        music_files = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f))]
                        if music_files:
                            random_file = random.choice(music_files)
                            logging.debug(f"Randomly selected music file: {random_file}")
                            music_file = os.path.join(music_dir, random_file)
                        else:
                            logging.warning("No music files found in the music directory.")
                            continue
                elif qr_data == "stop":
                    logging.info("Stopping playback.")
                    music_file="stop"
                    stop_vlc()
                    continue
                else:
                    music_file = os.path.join(music_dir, qr_data)
                
                # Check if the file exists
                if os.path.exists(music_file):
                    logging.info(f"Playing {music_file}")
                    # Load and play the music file in a loop
                    play_with_vlc(music_file)
                    music_file=""
                else:
                    logging.error(f"Error: {music_file} not found.")
    else:
        logging.error("Failed to read frame from camera.")

    # Wait for 0.5 seconds
    # logging.debug("Waiting for 0.5 seconds.")
    time.sleep(0.5)

# Release the camera and quit
logging.debug("Releasing camera.")
cap.release()
