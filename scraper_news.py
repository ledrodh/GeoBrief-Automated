from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random
import json
from datetime import datetime
import os

# --- CONFIGURAÇÃO DOS ALVOS (TARGETS) ---
TARGETS = [
    # --- Mídia Original ---
    {
        "name": "Reuters",
        "url": "https://www.reuters.com/world/",
        "link_keywords": ["/world/"]
    },
    {
        "name": "The Independent",
        "url": "https://www.independent.co.uk/news/world?CMP=ILC-refresh",
        "link_keywords": ["/news/world/"]
    },
    {
        "name": "The National UAE",
        "url": "https://www.thenationalnews.com/news/uae/",
        "link_keywords": ["/news/uae/"]
    },
    
    # --- Novos Alvos Adicionados ---
    {
        "name": "Defence Blog",
        "url": "https://defence-blog.com/",
        # Defence blog não usa categorias na URL, mas notícias sempre têm hifens (slugs)
        "link_keywords": ["-"] 
    },
    {
        "name": "BBC World",
        "url": "https://www.bbc.com/news/world",
        "link_keywords": ["/news/world"]
    },
    {
        "name": "Noticia Brasil (Mundo)",
        "url": "https://noticiabrasil.net.br/mundo/",
        "link_keywords": ["/mundo/"]
    },
    {
        "name": "Brookings",
        "url": "https://www.brookings.edu/",
        "link_keywords": ["/articles/", "/research/", "/blog/"]
    },
    {
        "name": "CFR (Council on Foreign Relations)",
        "url": "https://www.cfr.org/regions/global-commons",
        "link_keywords": [
            "topics/defense-and-security", 
            "diplomacy-and-international-institutions", 
            "topics/economics"
        ]
    },
    {
        "name": "CSIS (Center for Strategic and International Studies)",
        "url": "https://www.csis.org/topics/technology",
        "link_keywords": [
            "topics/geopolitics-and-international-security", 
            "topics/technology"
        ]
    }
]

MIN_ARTICLE_LENGTH = 250  # Mínimo de caracteres para salvar

def save_to_json(data):
    """Salva todos os dados em um único arquivo JSON do dia"""
    if not data:
        print("⚠️ Nenhum dado coletado.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"global_news_dump_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ [ARQUIVO SALVO] {os.path.abspath(filename)}")
        print(f"📊 Total de notícias: {len(data)}")
    except Exception as e:
        print(f"❌ Erro ao salvar JSON: {e}")

def run_scraper_pipeline():
    print("🚀 Iniciando Motor de Scraping Multi-Site Expandido...")
    
    all_news_results = []
    
    args = [
        "--disable-blink-features=AutomationControlled",
        "--start-maximized", 
        "--no-sandbox",
        "--headless=new" # Modo Stealth Silencioso
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=args)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()

        # --- LOOP PELOS SITES ---
        for site in TARGETS:
            print(f"\n" + "="*50)
            print(f"🌍 FONTE: {site['name']}")
            print(f"🔗 URL: {site['url']}")
            print("="*50)

            try:
                page.goto(site['url'], timeout=60000)
                time.sleep(5) # Espera um pouco mais para sites pesados

                # 1. SCROLL GENÉRICO
                print("🔄 Carregando feed...")
                for _ in range(3): 
                    page.keyboard.press("End")
                    time.sleep(2)
                
                # 2. COLETA DE LINKS INTELIGENTE (Suporta Multi-Keywords)
                print(f"🎣 Buscando links compatíveis...")
                
                # Pega todos os links da página
                links_elements = page.locator("a").all()
                
                unique_urls = set()
                articles_to_scrape = []

                for link in links_elements:
                    try:
                        href = link.get_attribute("href")
                        text = link.inner_text().strip()
                        
                        if href and len(text) > 10:
                            # Monta URL absoluta
                            if href.startswith('/'):
                                # Pega o domínio base corretamente
                                from urllib.parse import urlparse
                                parsed_uri = urlparse(site['url'])
                                base_domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
                                full_url = base_domain + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue # Ignora links javascript: ou mailto:

                            # --- FILTRO MULTI-KEYWORD ---
                            # Verifica se ALGUMA das palavras chaves está na URL
                            match_keyword = False
                            for keyword in site['link_keywords']:
                                if keyword in full_url:
                                    match_keyword = True
                                    break
                            
                            # Filtros adicionais de exclusão (lixo comum)
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

                print(f"📋 Encontrados {len(articles_to_scrape)} artigos potenciais.")

                # 3. EXTRAÇÃO DE CONTEÚDO (Limitado a 3 por site para teste rápido - REMOVA O SLICE EM PRODUÇÃO)
                # Dica: Para coletar tudo, mude de 'articles_to_scrape[:3]' para 'articles_to_scrape'
                for index, item in enumerate(articles_to_scrape[:3]): 
                    print(f"   [{index+1}] Lendo: {item['headline'][:40]}...")
                    
                    try:
                        page.goto(item['url'], timeout=45000)
                        
                        # Tenta remover popups comuns
                        try:
                            page.keyboard.press("Escape")
                        except:
                            pass

                        soup = BeautifulSoup(page.content(), 'html.parser')
                        
                        # Extração Genérica de Título
                        title_tag = soup.find('h1')
                        title = title_tag.get_text().strip() if title_tag else item['headline']
                        
                        # Extração Inteligente de Texto
                        # Alguns sites usam 'article', outros divs específicas. 
                        # Vamos focar em <p> que tenham texto substancial.
                        paragraphs = soup.find_all('p')
                        text_content = []
                        for p in paragraphs:
                            txt = p.get_text().strip()
                            # Filtra parágrafos de menu ou rodapé (< 60 chars)
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
                            print(f"      ✅ Sucesso ({len(full_text)} caracteres)")
                        else:
                            print(f"      ⚠️ Conteúdo curto ou protegido.")

                    except Exception as e:
                        print(f"      ❌ Erro: {e}")
                    
                    time.sleep(random.uniform(2, 5))

            except Exception as e:
                print(f"❌ Erro crítico em {site['name']}: {e}")

        browser.close()
        return all_news_results

if __name__ == "__main__":
    data = run_scraper_pipeline()
    save_to_json(data)