
import cv2
from pyzbar import pyzbar
import time
import os
import random
import subprocess
from datetime import datetime, timedelta

# Initialize the camera
cap = cv2.VideoCapture(0)

vlc_process = None

def play_with_vlc(file_path):
    global vlc_process
    # Stop old VLC instance
    if vlc_process and vlc_process.poll() is None:
        vlc_process.terminate()
    # Start new VLC in loop
    vlc_process = subprocess.Popen(["cvlc", "--loop", file_path])

def stop_vlc():
    global vlc_process
    if vlc_process and vlc_process.poll() is None:
        vlc_process.terminate()
        vlc_process = None

# Set to store previously scanned QR codes
last_qr_code = ""
last_random_trigger_time = datetime.min

# Directory where music files are stored
music_dir = "music"

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    if ret:
        # Decode QR codes
        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            # Get the data from the QR code
            qr_data = barcode.data.decode("utf-8")

            # If the QR code has not been scanned before
            if qr_data != last_qr_code:
                print(f"New QR code detected: {qr_data}")
                last_qr_code = qr_data

                if qr_data == "random":
                    last_qr_code = ""
                    if datetime.now() - last_random_trigger_time > timedelta(seconds=3):
                        last_random_trigger_time = datetime.now()
                        # random can be reused
                        music_files = [f for f in os.listdir(music_dir) if os.path.isfile(os.path.join(music_dir, f))]
                        if music_files:
                            random_file = random.choice(music_files)
                            music_file = os.path.join(music_dir, random_file)
                        else:
                            print("No music files found in the music directory.")
                            continue
                elif qr_data == "stop":
                    print("Stopping playback.")
                    music_file="stop"
                    stop_vlc()
                    continue
                
                # Check if the file exists
                if os.path.exists(music_file):
                    print(f"Playing {music_file}")
                    # Load and play the music file in a loop
                    play_with_vlc(music_file)
                    music_file=""
                else:
                    print(f"Error: {music_file} not found.")

    # Wait for 0.5 seconds
    time.sleep(0.5)

# Release the camera and quit
cap.release()
