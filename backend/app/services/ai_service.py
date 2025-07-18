# /backend/app/services/ai_service.py

import google.generativeai as genai
from typing import List, Dict, Any
from app.core.config import settings

# Inicializa a variável do modelo
model = None

# Tenta configurar a API ao iniciar o módulo
try:
    # Usando o nome do modelo que você confirmou estar disponível
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    # Configuração de segurança para permitir respostas menos restritivas
    # Útil para dados de negócios que podem ser falsamente sinalizados.
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Modelo de IA Gemini inicializado com sucesso.")

except Exception as e:
    print(f"❌ Erro ao configurar a API do Gemini: {e}")

def generate_analysis_from_data(user_question: str, system_data: str) -> str:
    """
    Recebe uma pergunta do usuário e os dados do sistema, envia para a IA 
    com um prompt aprimorado e retorna a resposta.
    """
    if not model:
        return "Erro: O modelo de IA não foi inicializado corretamente. Verifique a chave da API e a configuração do serviço no servidor."
     
    # Mega prompt aprimorado que ensina a IA a usar todos os dados
    prompt_template = f"""
    Você é a "Assistente de Análise Higiplas", uma IA especialista em gestão de estoque e análise de dados de negócios. Sua função é ajudar o gestor a entender os dados do sistema e tomar melhores decisões, o nome dado a você é Rozana.
     
    O gestor fez a seguinte pergunta: 
    "{user_question}"
     
    Para te ajudar a responder, você recebeu um JSON com três fontes de dados do sistema:
    1.  `estoque_atual_da_empresa`: A quantidade de cada produto em estoque neste momento, incluindo o estoque mínimo.
    2.  `resumo_historico_dos_produtos_mais_vendidos`: Um ranking dos produtos com maior volume de vendas ao longo do tempo.
    3.  `log_de_movimentacoes_recentes_ultimos_30_dias`: Um registro detalhado de todas as ENTRADAS e SAÍDAS dos últimos 30 dias. Este é o melhor indicador de demanda recente e velocidade de vendas.
    ---
    DADOS DO SISTEMA:
    {system_data}
    ---
     
    Instruções para sua resposta:
    1.  Cruze as informações das três fontes de dados para dar uma resposta completa e contextualizada.
    2.  Responda de forma clara, profissional e direta. Use Markdown (títulos com '#', negrito com '**', e listas com '-') para formatar sua resposta de forma legível.
    3.  Para perguntas sobre demanda ou velocidade de vendas, priorize a análise do `log_de_movimentacoes_recentes`. Para popularidade geral, use o `resumo_historico_dos_produtos_mais_vendidos`. Para disponibilidade, use o `estoque_atual`.
    4.  Se os dados não forem suficientes, explique o porquê e sugira uma pergunta mais específica.
    """
     
    try:
        print("[AI Service] Gerando conteúdo com a API do Gemini...")
        response = model.generate_content(prompt_template)
        
        # Bloco de tratamento de erro para respostas bloqueadas
        try:
            print("[AI Service] Resposta da IA recebida.")
            return response.text
        except ValueError:
            print(f"❌ Resposta da IA bloqueada. Feedback do prompt: {response.prompt_feedback}")
            return f"A resposta da IA foi bloqueada por razões de segurança. Verifique a pergunta ou os dados enviados. Motivo do bloqueio: {response.prompt_feedback}"

    except Exception as e:
        print(f"❌ Erro na comunicação com a API do Gemini: {e}")
        return f"Ocorreu um erro ao comunicar com a IA: {e}"