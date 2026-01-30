import json
import asyncio
from telethon import TelegramClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

# CRITICAL: Never hardcode credentials in public code.
# Ensure API_ID and API_HASH are in your .env file.
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# --- TARGET CHANNELS (DEMO) ---
# Generic, high-profile sources for the public portfolio.
TARGET_CHANNELS = [
    'TheEconomist',    # Global Economics/Politics
    'nytimes',         # The New York Times
    'bloomberg',       # Markets & Geopolitics
    'WSJ'              # Wall Street Journal
]

# Configuration
LIMIT_MESSAGES = 10  # How many messages to fetch per channel
MIN_CHARS = 100      # Ignore short messages

async def get_telegram_news():
    print("🚀 Starting Telegram Scraper...")

    if not API_ID or not API_HASH:
        print("❌ Error: API_ID or API_HASH not found in .env file.")
        return []
    
    # Create the session (creates a .session file locally)
    # Note: Ensure the session name matches what you uploaded or Gitignored
    client = TelegramClient('user_session', int(API_ID), API_HASH)
    
    news_data = []
    
    await client.start()
    print("✅ Login successful!")

    for channel in TARGET_CHANNELS:
        print(f"\n📡 Scanning channel: {channel}...")
        
        try:
            # Get channel entity (resolves @name)
            entity = await client.get_entity(channel)
            
            # Iterate over messages
            async for message in client.iter_messages(entity, limit=LIMIT_MESSAGES):
                
                if message.text and len(message.text) > MIN_CHARS:
                    # Format date
                    date_str = message.date.isoformat()
                    
                    # Create a fake title (first 10 words)
                    fake_title = " ".join(message.text.split()[:10]) + "..."
                    
                    # Direct link to message
                    msg_link = f"https://t.me/{channel}/{message.id}"

                    news_data.append({
                        "source": f"Telegram ({channel})",
                        "title": fake_title,
                        "url": msg_link,
                        "scraped_at": datetime.now().isoformat(),
                        "content": message.text
                    })
            
            print(f"   ✅ Collected {len(news_data)} valid posts so far.")

        except Exception as e:
            print(f"   ❌ Error scanning {channel}: {e}")

    await client.disconnect()
    return news_data

def save_to_json(data):
    if not data: return
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"telegram_dump_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n💾 File saved: {filename}")

# --- EXECUTION ---
if __name__ == "__main__":
    # Python requires a loop to run async functions
    data = asyncio.run(get_telegram_news())
    save_to_json(data)