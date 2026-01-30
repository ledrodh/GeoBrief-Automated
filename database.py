import sqlite3
from datetime import datetime

DB_NAME = "bot_memory.db"

def init_db():
    """Cria a tabela no banco se ela não existir"""
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
            print("💾 Banco de dados inicializado/verificado.")
    except Exception as e:
        print(f"❌ Erro ao iniciar banco: {e}")

def is_url_processed(url):
    """Retorna True se a URL já existe no banco, False se for nova"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM history WHERE url = ?", (url,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"❌ Erro ao verificar URL: {e}")
        return False # Na dúvida, processa de novo para não perder info

def mark_url_as_processed(url, source):
    """Salva a URL no banco para não processar novamente"""
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
        print(f"❌ Erro ao salvar URL: {e}")

# Teste rápido se rodar o arquivo direto
if __name__ == "__main__":
    init_db()
    # Teste
    test_url = "https://exemplo.com/noticia-teste"
    if not is_url_processed(test_url):
        print("Link novo! Salvando...")
        mark_url_as_processed(test_url, "Teste")
    else:
        print("Link já processado.")