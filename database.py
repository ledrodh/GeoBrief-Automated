import sqlite3
from datetime import datetime

DB_NAME = "bot_memory.db"

def init_db():
    """Initializes the database table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    url TEXT PRIMARY KEY,
                    source TEXT,
                    processed_at DATETIME
                )
            """)
            conn.commit()
            print("💾 Database initialized/verified.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

def is_url_processed(url):
    """Returns True if URL exists in DB, False otherwise."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM history WHERE url = ?", (url,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"❌ Error checking URL: {e}")
        return False # Fallback: process again to ensure data integrity

def mark_url_as_processed(url, source):
    """Saves URL to DB to prevent re-processing."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT OR IGNORE INTO history (url, source, processed_at) VALUES (?, ?, ?)",
                (url, source, now)
            )
            conn.commit()
    except Exception as e:
        print(f"❌ Error saving URL: {e}")

# Quick test if run directly
if __name__ == "__main__":
    init_db()
    # Test case
    test_url = "https://example.com/test-news"
    if not is_url_processed(test_url):
        print("New link detected! Saving...")
        mark_url_as_processed(test_url, "Test")
    else:
        print("Link already processed.")