
import cv2
from pyzbar import pyzbar
import time
import os
import random
import subprocess
from datetime import datetime, timedelta
import logging
import threading
import database

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database
database.init_db()

# Initialize the camera
logging.debug("Initializing camera...")
cap = cv2.VideoCapture("/dev/video10")
if not cap.isOpened():
    logging.error("Cannot open camera")
    exit()

vlc_process = None
monitor_thread = None
stop_monitor_event = threading.Event()

def monitor_playback(directory_qr_id, stop_event):
    """Monitors the currently playing song and updates the database."""
    last_known_song = None
    logging.info(f"Monitoring playback for directory: {directory_qr_id}")
    while not stop_event.is_set():
        try:
            # Get the full path of the currently playing song
            proc = subprocess.run(
                ["playerctl", "metadata", "xesam:url"],
                capture_output=True, text=True, check=True
            )
            current_song_url = proc.stdout.strip()

            if current_song_url:
                current_song_path = current_song_url.replace('file://', '')
                if current_song_path != last_known_song:
                    last_known_song = current_song_path
                    logging.info(f"New song detected: {current_song_path}")
                    database.update_last_song(directory_qr_id, current_song_path)
        except subprocess.CalledProcessError:
            # This can happen if the player is stopped or not running
            logging.debug("Player not running or no metadata available.")
            # If the monitor was not told to stop, it means playback ended unexpectedly.
            if not stop_event.is_set():
                logging.info("Playback seems to have ended. Stopping monitoring.")
                break # Exit the monitoring loop
        
        # Wait for a bit before checking again
        time.sleep(2)
    logging.info(f"Stopped monitoring playback for directory: {directory_qr_id}")


def play_with_vlc(file_path, loop=False):
    """Plays a single file with VLC."""
    global vlc_process
    logging.debug(f"Attempting to play {file_path} with VLC.")
    
    cmd = ["cvlc"]
    if loop:
        cmd.append("--loop")
    cmd.append(file_path)
    
    logging.debug(f"Starting new VLC process with command: {' '.join(cmd)}")
    vlc_process = subprocess.Popen(cmd)

def stop_vlc():
    global monitor_thread, stop_monitor_event, vlc_process
    logging.debug("Stopping VLC playback and monitoring.")
    
    # Stop the monitor thread first
    if monitor_thread and monitor_thread.is_alive():
        stop_monitor_event.set()
        monitor_thread.join()
    
    # Stop the player
    status_proc = subprocess.run(['playerctl', 'status'], capture_output=True, text=True)
    if status_proc.returncode == 0 and "No players found" not in status_proc.stdout:
         subprocess.run(["playerctl", "stop"])

    # Clean up VLC process handle if it exists
    if vlc_process and vlc_process.poll() is None:
        vlc_process.terminate()
        vlc_process.wait()
    vlc_process = None


# Set to store previously scanned QR codes
last_qr_code = ""
last_random_trigger_time = datetime.min
last_next_trigger_time = datetime.min
last_previous_trigger_time = datetime.min

# Directory where music files are stored
music_dir = "music"
logging.debug(f"Music directory set to: {music_dir}")

while True:
    ret, frame = cap.read()

    if ret:
        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            qr_data = barcode.data.decode("utf-8").replace("http://", "")
            logging.debug(f"Decoded QR data: {qr_data}")

            if qr_data != last_qr_code:
                logging.info(f"New QR code detected: {qr_data}")
                last_qr_code = qr_data

                if qr_data == "random":
                    last_qr_code = ""
                    if datetime.now() - last_random_trigger_time > timedelta(seconds=3):
                        last_random_trigger_time = datetime.now()
                        stop_vlc()
                        logging.debug("Random QR code triggered.")
                        all_music_files = [os.path.join(root, f) for root, _, files in os.walk(music_dir) for f in files]
                        if all_music_files:
                            random_file = random.choice(all_music_files)
                            logging.debug(f"Randomly selected music file: {random_file}")
                            play_with_vlc(random_file, loop=True)
                        else:
                            logging.warning("No music files found in the music directory.")
                    continue
                elif qr_data == "stop":
                    logging.info("Stopping playback.")
                    stop_vlc()
                    continue
                elif qr_data == "next":
                    last_qr_code = ""
                    if datetime.now() - last_next_trigger_time > timedelta(seconds=5):
                        last_next_trigger_time = datetime.now()
                        logging.info("Playing next track.")
                        subprocess.run(["playerctl", "next", "-p", "vlc"])
                    continue
                elif qr_data == "previous":
                    last_qr_code = ""
                    if datetime.now() - last_previous_trigger_time > timedelta(seconds=5):
                        last_previous_trigger_time = datetime.now()
                        logging.info("Playing previous track.")
                        subprocess.run(["playerctl", "previous", "-p", "vlc"])
                    continue
                
                music_path = os.path.join(music_dir, qr_data)
                
                if os.path.exists(music_path):
                    stop_vlc()
                    if os.path.isdir(music_path):
                        logging.info(f"Directory QR code detected: {qr_data}")
                        
                        # Start playing the whole directory
                        vlc_process = subprocess.Popen(["cvlc", music_path])
                        
                        # Start monitoring
                        stop_monitor_event.clear()
                        monitor_thread = threading.Thread(target=monitor_playback, args=(qr_data, stop_monitor_event))
                        monitor_thread.start()

                        # Give VLC a moment to start up
                        time.sleep(1)

                        # Find song to resume from
                        last_song = database.get_last_song(qr_data)
                        music_files = sorted([os.path.join(music_path, f) for f in os.listdir(music_path) if os.path.isfile(os.path.join(music_path, f))])
                        
                        song_to_start_with = None
                        if last_song and music_files:
                             try:
                                 last_played_index = music_files.index(last_song)
                                 start_index = (last_played_index + 1) % len(music_files)
                                 song_to_start_with = music_files[start_index]
                                 logging.info(f"Resuming from song after {last_song}")
                             except ValueError:
                                 logging.warning(f"Last played song {last_song} not found. Starting from beginning.")
                                 song_to_start_with = music_files[0]
                        
                        if song_to_start_with:
                            logging.info(f"Telling player to open {song_to_start_with}")
                            # Use playerctl to open the specific song
                            subprocess.run(["playerctl", "open", f"file://{os.path.abspath(song_to_start_with)}"])

                    elif os.path.isfile(music_path):
                        logging.info(f"File QR code detected: {qr_data}")
                        play_with_vlc(music_path, loop=True)
                else:
                    logging.error(f"Error: {music_path} not found.")
            
    time.sleep(0.5)

# Release the camera and quit
logging.debug("Releasing camera.")
stop_vlc()
cap.release()
