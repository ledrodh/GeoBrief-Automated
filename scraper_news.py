from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime
import os
from urllib.parse import urlparse

# --- TARGET CONFIGURATION  ---
# These are generic, high-traffic global sites to demonstrate capability.
TARGETS = [
    {
        "name": "BBC World",
        "url": "https://www.bbc.com/news/world",
        "link_keywords": ["/news/world"]
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/news/",
        "link_keywords": ["/news/20"] # Al Jazeera usually has dates in URLs
    }
]

MIN_ARTICLE_LENGTH = 250  # Minimum characters to be considered valid
MAX_ARTICLES_PER_SITE = 5 # Limit for demo purposes

def save_to_json(data):
    """Saves raw data to a JSON file (useful for debugging)."""
    if not data:
        print("⚠️ No data collected.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"global_news_dump_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ [FILE SAVED] {os.path.abspath(filename)}")
        print(f"📊 Total items: {len(data)}")
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")

def run_scraper_pipeline():
    print("🚀 Starting Multi-Site Web Scraper...")
    
    all_news_results = []
    
    args = [
        "--disable-blink-features=AutomationControlled",
        "--start-maximized", 
        "--no-sandbox",
        "--headless=new" # Stealth Mode
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=args)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        
        # Anti-detect script
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()

        # --- SITE LOOP ---
        for site in TARGETS:
            print(f"\n" + "="*50)
            print(f"🌍 SOURCE: {site['name']}")
            print(f"🔗 URL: {site['url']}")
            print("="*50)

            try:
                page.goto(site['url'], timeout=60000)
                time.sleep(5) 

                # 1. GENERIC SCROLL
                print("🔄 Loading feed...")
                for _ in range(3): 
                    page.keyboard.press("End")
                    time.sleep(2)
                
                # 2. SMART LINK HARVESTING
                print(f"🎣 Harvesting links...")
                
                links_elements = page.locator("a").all()
                
                unique_urls = set()
                articles_to_scrape = []

                for link in links_elements:
                    try:
                        href = link.get_attribute("href")
                        text = link.inner_text().strip()
                        
                        if href and len(text) > 10:
                            # Construct absolute URL
                            if href.startswith('/'):
                                parsed_uri = urlparse(site['url'])
                                base_domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                                full_url = base_domain + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue 

                            # --- KEYWORD FILTER ---
                            match_keyword = False
                            for keyword in site['link_keywords']:
                                if keyword in full_url:
                                    match_keyword = True
                                    break
                            
                            # Exclusion filters
                            exclusion_terms = ["/video/", "/live/", "/author/", "/category/", "contact", "about"]
                            is_excluded = any(term in full_url for term in exclusion_terms)

                            if match_keyword and not is_excluded and full_url not in unique_urls:
                                unique_urls.add(full_url)
                                articles_to_scrape.append({
                                    "headline": text,
                                    "url": full_url,
                                    "source": site['name']
                                })
                    except:
                        continue

                print(f"📋 Found {len(articles_to_scrape)} potential articles.")

                # 3. CONTENT EXTRACTION
                # Limited by MAX_ARTICLES_PER_SITE for the public demo
                for index, item in enumerate(articles_to_scrape[:MAX_ARTICLES_PER_SITE]): 
                    print(f"   [{index+1}] Reading: {item['headline'][:40]}...")
                    
                    try:
                        page.goto(item['url'], timeout=45000)
                        
                        # Close popups
                        try:
                            page.keyboard.press("Escape")
                        except:
                            pass

                        soup = BeautifulSoup(page.content(), 'html.parser')
                        
                        # Generic Title Extraction
                        title_tag = soup.find('h1')
                        title = title_tag.get_text().strip() if title_tag else item['headline']
                        
                        # Smart Text Extraction
                        paragraphs = soup.find_all('p')
                        text_content = []
                        for p in paragraphs:
                            txt = p.get_text().strip()
                            if len(txt) > 60: text_content.append(txt)
                        
                        full_text = "\n\n".join(text_content)
                        
                        if len(full_text) > MIN_ARTICLE_LENGTH:
                            all_news_results.append({
                                "source": item['source'],
                                "title": title,
                                "url": item['url'],
                                "scraped_at": datetime.now().isoformat(),
                                "content": full_text
                            })
                            print(f"      ✅ Success ({len(full_text)} chars)")
                        else:
                            print(f"      ⚠️ Content too short or protected.")

                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                    
                    time.sleep(random.uniform(2, 5))

            except Exception as e:
                print(f"❌ Critical error in {site['name']}: {e}")

        browser.close()
        return all_news_results

if __name__ == "__main__":
    data = run_scraper_pipeline()
    save_to_json(data)