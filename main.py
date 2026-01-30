import asyncio
import os
from datetime import datetime
from database import init_db, is_url_processed, mark_url_as_processed
import scraper_news      
import scraper_telegram  
import analyst_ai        
import notifier  
def main():
    print("🤖 INICIANDO O SISTEMA THE EYES...")
    print("-" * 40)

    # 1. Garante que o banco existe
    init_db()

    # 2. Coleta de Dados Brutos
    print("\n📡 Fase 1: Coleta de Dados")
    
    # Coleta Web
    web_news = scraper_news.run_scraper_pipeline()
    
    # Coleta Telegram (Async)
    telegram_news = asyncio.run(scraper_telegram.get_telegram_news())
    
    all_raw_data = web_news + telegram_news
    print(f"📊 Total coletado (bruto): {len(all_raw_data)}")

    # 3. Filtragem (O "Peneira")
    print("\n🔍 Fase 2: Filtragem de Duplicatas")
    new_data = []

    for item in all_raw_data:
        if not is_url_processed(item['url']):
            new_data.append(item)
        else:
            # Opcional: printar duplicatas (pode poluir o log)
            # print(f"   Ignorando duplicata: {item['title'][:30]}...")
            pass

    if not new_data:
        print("💤 Nenhuma notícia nova encontrada desde a última execução.")
        print("🏁 Sistema finalizado.")
        return

    print(f"✨ Notícias inéditas para análise: {len(new_data)}")

    # 4. Análise de Inteligência (IA)
    print("\n🧠 Fase 3: Processamento Cognitivo (Gemini)")
    
    # Pequena adaptação: Vamos passar os dados direto para a função, 
    # sem precisar salvar e ler JSON do disco (mais rápido).
    # *Nota: Precisamos ajustar o analyst_ai.py levemente para aceitar lista, 
    # mas por enquanto vamos salvar um JSON temporário para compatibilidade*
    
    temp_json_name = "temp_processing_queue.json"
    scraper_news.save_to_json(new_data) # Reusa a função de salvar do scraper
    # Renomeia para o analyst achar (ou ajustamos o analyst para pegar o mais novo)
    # Mas o seu analyst_ai já pega o arquivo mais recente! Então está ok.

    report_text = analyst_ai.generate_daily_briefing(direct_data=new_data)


    if report_text:
        print("\n💾 Fase 4: Atualizando Memória de Longo Prazo")
        
        # O loop FOR deve estar DENTRO do IF (recuado)
        for item in new_data:
            mark_url_as_processed(item['url'], item.get('source', 'Unknown'))
        print("✅ Banco de dados atualizado.")
        
        # O envio também deve estar DENTRO do IF
        print("\n📨 Fase 5: Notificação")
        notifier.send_telegram_report(report_text)
        
    else:
        # Este ELSE agora funciona porque está alinhado com o IF
        print("❌ Falha ao gerar relatório. Banco de dados NÃO foi atualizado.")

    print("\n🏁 Execução finalizada com sucesso.")

# Remova os espaços extras antes do if e do main()
if __name__ == "__main__":
    main()