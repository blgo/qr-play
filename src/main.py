
import cv2
from pyzbar import pyzbar
import pygame
import time
import os

# Initialize the camera
cap = cv2.VideoCapture(0)

# Initialize pygame
pygame.init()

# Set to store previously scanned QR codes
scanned_codes = set()

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
            if qr_data not in scanned_codes:
                print(f"New QR code detected: {qr_data}")
                scanned_codes.add(qr_data)

                # Construct the full path to the music file
                music_file = os.path.join(music_dir, qr_data)

                # Check if the file exists
                if os.path.exists(music_file):
                    print(f"Playing {music_file}")
                    # Load and play the music file in a loop
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                else:
                    print(f"Error: {music_file} not found.")

    # Wait for 0.5 seconds
    time.sleep(0.5)

# Release the camera and quit pygame
cap.release()
pygame.quit()
