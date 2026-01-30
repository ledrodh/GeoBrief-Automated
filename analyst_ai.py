import google.generativeai as genai
import os
import json
import glob
from dotenv import load_dotenv
from datetime import datetime

# Carrega a API KEY
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ ERRO: Chave não encontrada no .env")

genai.configure(api_key=api_key)

# 1. DEFINA A CONFIGURAÇÃO PRIMEIRO (Antes de usar)
generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# 2. DEFINA O NOME DO MODELO (Corrigido para 1.5, pois 2.5 não existe ainda)
MODEL_NAME = "models/gemini-2.5-flash" 

print(f"🤖 Usando modelo: {MODEL_NAME}")

# 3. AGORA SIM, CRIE O MODELO
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config=generation_config, # Agora a variável já existe!
    system_instruction="""
    Você é um Analista de Geopolítica Sênior e Especialista em Inteligência.
    Sua missão é ler notícias cruas de diversas fontes e produzir um relatório executivo de alta qualidade (Briefing Diário).
    
    DIRETRIZES DE ANÁLISE:
    1. FILTRO DE RUÍDO: Ignore fofocas, esportes ou crimes locais irrelevantes.
    2. FOCO: Priorize conflitos bélicos, movimentos militares, decisões econômicas de blocos (BRICS, UE, OTAN) e crises humanitárias.
    3. SÍNTESE: Cruze as informações. Se Reuters e Telegram falam do mesmo evento, combine os dados.
    4. IMPARCIALIDADE: Mantenha tom neutro, técnico e direto.
    """
)
# ... (O resto do código permanece igual: load_latest_json_files, generate_daily_briefing, etc.)
def load_latest_json_files():
    """Busca os arquivos JSON mais recentes gerados pelos scrapers"""
    # Pega o arquivo mais recente que começa com 'global_news_'
    news_files = sorted(glob.glob("global_news_dump_*.json"), key=os.path.getmtime)
    telegram_files = sorted(glob.glob("telegram_dump_*.json"), key=os.path.getmtime)
    
    data_content = []

    if news_files:
        latest_news = news_files[-1]
        print(f"📂 Carregando Notícias Web: {latest_news}")
        with open(latest_news, 'r', encoding='utf-8') as f:
            data_content.extend(json.load(f))
    
    if telegram_files:
        latest_telegram = telegram_files[-1]
        print(f"📂 Carregando Telegram: {latest_telegram}")
        with open(latest_telegram, 'r', encoding='utf-8') as f:
            data_content.extend(json.load(f))
            
    return data_content

def generate_daily_briefing(direct_data=None):
    print("🧠 Iniciando Análise de Inteligência com Gemini...")
    
    # 1. Decide a fonte dos dados (Memória ou Arquivo)
    if direct_data:
        raw_data = direct_data
        print(f"📂 Usando {len(raw_data)} itens passados diretamente pela memória.")
    else:
        raw_data = load_latest_json_files()
    
    # 2. Se não tiver dados, para tudo
    if not raw_data:
        print("⚠️ Nenhum dado encontrado para analisar.")
        return None

    # ### O FIX ESTÁ AQUI ###
    # Precisamos converter a lista (raw_data) em String (data_str) 
    # ANTES de usar no user_prompt
    try:
        data_str = json.dumps(raw_data, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Erro ao converter dados para texto: {e}")
        return None

    # 3. Monta o Prompt
    user_prompt = f"""
    Aqui estão os dados brutos coletados hoje ({datetime.now().strftime('%d/%m/%Y')}):
    
    {data_str}
    
    ---
    TAREFA:
    Escreva um Resumo Executivo Diário em Português (PT-BR).
    
    ESTRUTURA DESEJADA:
     🌍 RELATÓRIO DE INTELIGÊNCIA GLOBAL - {datetime.now().strftime('%d/%m/%Y')}
    
     🔥 Destaques Críticos (Manchetes de alto impacto)
     [Tópico 1]: Resumo de 2 linhas.
    
     ⚔️ Conflitos e Segurança (Defesa, Guerras, Terrorismo)
    (Agrupe as notícias por região ou conflito)
    
     💰 Geoeconomia e Diplomacia
    (Acordos, sanções, blocos econômicos)
    
     👁️ Radar OSINT (Informações do Telegram/Fontes não oficiais)
    
     🔗 Fontes Utilizadas
    """

    print("⏳ Enviando dados para o Gemini (pode levar alguns segundos)...")
    
    try:
        response = model.generate_content(user_prompt)
        report_text = response.text
        
        # Salva o relatório
        filename = f"RELATORIO_FINAL_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
            
        print(f"\n✅ Relatório Gerado com Sucesso: {filename}")
        # print(report_text) # Descomente se quiser ver no terminal
        return report_text

    except Exception as e:
        print(f"❌ Erro na geração da IA: {e}")
        return None