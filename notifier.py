import requests
import os
import textwrap
from dotenv import load_dotenv

# Load configuration
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_report(message_text):
    """Sends the report to Telegram, splitting it into chunks if necessary."""
    
    if not message_text:
        print("⚠️ Notifier: Empty text, nothing to send.")
        return

    if not TOKEN or not CHAT_ID:
        print("❌ Notifier: TOKEN or CHAT_ID not found in .env")
        return

    print("📨 Sending report to Telegram...")

    # Telegram has a hard limit of 4096 chars per message.
    # Splitting into 4000-char chunks to be safe.
    chunks = textwrap.wrap(message_text, width=4000, replace_whitespace=False)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown" # Tries to format bold/titles
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status() 
            print(f"   ✅ Part {i+1}/{len(chunks)} sent.")
            
        except requests.exceptions.HTTPError:
            # Fallback: If Markdown fails (due to special chars), resend as plain text
            print(f"   ⚠️ Formatting error (Markdown). Resending as plain text...")
            payload.pop("parse_mode") 
            requests.post(url, json=payload)
            
        except Exception as e:
            print(f"   ❌ Failed to send part {i+1}: {e}")

if __name__ == "__main__":
    # Simple connection test
    send_telegram_report("🤖 GeoBrief System Test: Verification message.")