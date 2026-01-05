
import sqlite3
import logging

DB_PATH = '/home/appuser/db/qr_player.db'

def init_db():
    """Initializes the database and creates the playback_state table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS playback_state (
                    qr_code_id TEXT PRIMARY KEY,
                    last_song_path TEXT NOT NULL
                )
            ''')
            conn.commit()
            logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

def get_last_song(qr_code_id):
    """Gets the last played song for a given QR code ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_song_path FROM playback_state WHERE qr_code_id = ?", (qr_code_id,))
            result = cursor.fetchone()
            if result:
                logging.debug(f"Found last song for {qr_code_id}: {result[0]}")
                return result[0]
            else:
                logging.debug(f"No last song found for {qr_code_id}")
                return None
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None

def update_last_song(qr_code_id, song_path):
    """Updates the last played song for a given QR code ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO playback_state (qr_code_id, last_song_path)
                VALUES (?, ?)
            ''', (qr_code_id, song_path))
            conn.commit()
            logging.debug(f"Updated last song for {qr_code_id} to {song_path}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
