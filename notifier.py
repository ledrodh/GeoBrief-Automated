import requests
import os
import textwrap
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_report(message_text):
    """Envia o relatório para o Telegram, dividindo em partes se necessário."""
    
    if not message_text:
        print("⚠️ Notifier: Texto vazio, nada enviado.")
        return

    if not TOKEN or not CHAT_ID:
        print("❌ Notifier: TOKEN ou CHAT_ID não configurados no .env")
        return

    print("📨 Enviando relatório para o Telegram...")

    # O Telegram tem limite de 4096 caracteres por mensagem.
    # Vamos dividir o texto em blocos de 4000 para garantir.
    chunks = textwrap.wrap(message_text, width=4000, replace_whitespace=False)

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": CHAT_ID,
            "text": chunk,
            # 'Markdown' é chato com caracteres especiais. 
            # Se der erro, remova a linha abaixo para enviar como texto puro.
            "parse_mode": "Markdown" 
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status() # Lança erro se não for 200 OK
            print(f"   ✅ Parte {i+1}/{len(chunks)} enviada.")
            
        except requests.exceptions.HTTPError as e:
            # Se der erro de Markdown (comum se tiver * ou _ no lugar errado),
            # tenta reenviar como texto puro (fallback de segurança)
            print(f"   ⚠️ Erro de formatação (Markdown). Reenviando como texto puro...")
            payload.pop("parse_mode") 
            requests.post(url, json=payload)
            
        except Exception as e:
            print(f"   ❌ Falha ao enviar parte {i+1}: {e}")

if __name__ == "__main__":
    # Teste simples
    send_telegram_report("🤖 Teste do Sistema The Eyes: Mensagem de verificação.")