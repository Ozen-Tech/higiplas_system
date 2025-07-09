import google.generativeai as genai 
from typing import List, Dict, Any
from app.core.config import settings

 # Configura a API uma vez, quando o módulo é carregado.
try:
     genai.configure(api_key=settings.GOOGLE_API_KEY)
     model = genai.GenerativeModel('gemini-2.0-flash') # Modelo rápido e eficiente
     print("✅ Modelo de IA Gemini inicializado com sucesso.")
except Exception as e:
     print(f"❌ Erro ao configurar a API do Gemini: {e}")
     model = None

def generate_analysis_from_data(user_question: str, system_data: str) -> str:
     """
     Função genérica para enviar uma pergunta e dados contextuais para a IA.
     """
     if not model:
         return "Erro: O modelo de IA não foi inicializado corretamente. Verifique a chave da API no servidor."
     
     # Este é o nosso "Mega Prompt". É a instrução principal para a IA.
     prompt_template = f"""
     Você é o "Assistente de Análise Higiplas", uma IA especialista em gestão de estoque e análise de dados de negócios. 
     Sua função é ajudar o gestor a entender os dados do sistema e tomar melhores decisões.
     
     O gestor fez a seguinte pergunta: 
     "{user_question}"
     
     Para te ajudar a responder, aqui estão os dados relevantes do sistema no momento da pergunta. Use-os para basear sua resposta.
     ---
     DADOS DO SISTEMA:
     {system_data}
     ---
     
     Instruções para sua resposta:
     1. Responda de forma clara, profissional e direta.
     2. Utilize o formato Markdown para melhorar a legibilidade (use títulos, negrito e listas).
     3. Se os dados fornecidos não forem suficientes para responder à pergunta, explique o motivo e sugira que tipo de dado seria necessário.
     4. Se a pergunta for fora do escopo de gestão de estoque, recuse educadamente.
     """
     
     try:
         response = model.generate_content(prompt_template)
         return response.text
     except Exception as e:
         return f"Ocorreu um erro ao comunicar com a IA: {e}"
 