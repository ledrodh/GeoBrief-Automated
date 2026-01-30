import json
import asyncio
from telethon import TelegramClient
from datetime import datetime, timezone
import os

# --- SUAS CREDENCIAIS AQUI ---
API_ID = 38822425  
API_HASH = 'a34bb33f0841ca1ba7ef316132e50c58' 

# --- CANAIS ALVO ---
# Você pode colocar o @nome_do_canal ou o link t.me
TARGET_CHANNELS = [
    'armillary',    # Exemplo: Geopolítica
    'belllingcat',         # Exemplo: Investigação
    'TheEconomist',        # Exemplo: Notícias
    'geopolitics_prime',
    'canalartedaguerra',
    'GeopoliticaMundialVerdadeiro',
    'SputnikBrasil',
    'GeneralMCNews'
                                # Canal oficial da Reuters (se houver)
]

# Configuração
LIMIT_MESSAGES = 10  # Quantas mensagens pegar por canal
MIN_CHARS = 100      # Ignorar mensagens curtas (tipo "bom dia")

async def get_telegram_news():
    print("🚀 Iniciando Coleta do Telegram...")
    
    # Cria a sessão (cria um arquivo .session na pasta para salvar o login)
    client = TelegramClient('minha_sessao_telegram', API_ID, API_HASH)
    
    news_data = []
    
    await client.start()
    print("✅ Login efetuado com sucesso!")

    for channel in TARGET_CHANNELS:
        print(f"\n📡 Lendo canal: {channel}...")
        
        try:
            # Pega a entidade do canal (resolve o @nome)
            entity = await client.get_entity(channel)
            
            # Itera sobre as últimas mensagens
            async for message in client.iter_messages(entity, limit=LIMIT_MESSAGES):
                
                if message.text and len(message.text) > MIN_CHARS:
                    # Formata a data
                    date_str = message.date.isoformat()
                    
                    # Cria um título fake (primeiras 10 palavras)
                    fake_title = " ".join(message.text.split()[:10]) + "..."
                    
                    # Cria o link direto para a mensagem
                    msg_link = f"https://t.me/{channel}/{message.id}"

                    news_data.append({
                        "source": f"Telegram ({channel})",
                        "title": fake_title,
                        "url": msg_link,
                        "scraped_at": datetime.now().isoformat(),
                        "content": message.text
                    })
            
            print(f"   ✅ Coletados {len(news_data)} posts válidos até agora.")

        except Exception as e:
            print(f"   ❌ Erro ao ler canal {channel}: {e}")

    await client.disconnect()
    return news_data

def save_to_json(data):
    if not data: return
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"telegram_dump_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n💾 Arquivo salvo: {filename}")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # O Python precisa de um loop para rodar funções async
    data = asyncio.run(get_telegram_news())
    save_to_json(data)