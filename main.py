import asyncio
import os
from datetime import datetime

# Local modules
from database import init_db, is_url_processed, mark_url_as_processed
import scraper_news      
import scraper_telegram  
import analyst_ai        
import notifier  

def main():
    print("🤖 STARTING GEOBRIEF AI SYSTEM...")
    print("-" * 40)

    # 1. Initialize Database
    init_db()

    # 2. Data Collection
    print("\n📡 Phase 1: Data Collection")
    
    # Web Scraping
    web_news = scraper_news.run_scraper_pipeline()
    
    # Telegram Scraping (Async)
    telegram_news = asyncio.run(scraper_telegram.get_telegram_news())
    
    all_raw_data = web_news + telegram_news
    print(f"📊 Total raw items: {len(all_raw_data)}")

    # 3. Filtering (Deduplication)
    print("\n🔍 Phase 2: Deduplication")
    new_data = []

    for item in all_raw_data:
        if not is_url_processed(item['url']):
            new_data.append(item)
        else:
            # Pass on duplicates
            pass

    if not new_data:
        print("💤 No new data found since last run.")
        print("🏁 System finished.")
        return

    print(f"✨ New items for analysis: {len(new_data)}")

    # 4. AI Analysis
    print("\n🧠 Phase 3: Cognitive Processing (Gemini)")
    
    # Save a temp file for debugging/logging history
    scraper_news.save_to_json(new_data) 

    # Process data directly from memory
    report_text = analyst_ai.generate_daily_briefing(direct_data=new_data)

    # 5. DB Update & Notification
    if report_text:
        print("\n💾 Phase 4: Updating Long-Term Memory")
        
        for item in new_data:
            mark_url_as_processed(item['url'], item.get('source', 'Unknown'))
        print("✅ Database updated.")
        
        print("\n📨 Phase 5: Notification")
        notifier.send_telegram_report(report_text)
        
    else:
        print("❌ Failed to generate report. Database NOT updated.")

    print("\n🏁 Execution finished successfully.")

if __name__ == "__main__":
    main()