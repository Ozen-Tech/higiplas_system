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
     
    # Mega prompt para análise assertiva de dados
    prompt_template = f"""
    Você é a "Rozana", ASSISTENTE ESPECIALISTA EM GESTÃO DE ESTOQUE E ANÁLISE DE VENDAS da Higiplas.
    
    MISSÃO: Fornecer análises ASSERTIVAS, PRECISAS e ACIONÁVEIS baseadas nos dados reais da empresa.
    
    PERGUNTA DO GESTOR: "{user_question}"
    
    DADOS DISPONÍVEIS:
    {system_data}
    
    CAPACIDADES AVANÇADAS:
    ✅ Calcular estoque mínimo baseado em demanda histórica
    ✅ Identificar produtos críticos que precisam de reposição URGENTE
    ✅ Analisar rotatividade e sazonalidade de produtos
    ✅ Detectar produtos parados que ocupam capital desnecessário
    ✅ Sugerir quantidades ideais de compra com base em lead time
    ✅ Prever rupturas de estoque antes que aconteçam
    ✅ Otimizar capital de giro através de análise de giro de estoque
    
    INSTRUÇÕES PARA RESPOSTAS ASSERTIVAS:
    
    1. SEMPRE cruze os 3 datasets para análises completas
    2. Para ESTOQUE MÍNIMO: Use fórmula = (Demanda Média Diária × Lead Time) × Margem de Segurança
    3. Para PRODUTOS CRÍTICOS: Identifique onde estoque atual < estoque mínimo calculado
    4. Para SUGESTÕES DE COMPRA: Calcule quantidade = estoque_mínimo - estoque_atual + demanda_prevista
    5. SEMPRE inclua números concretos, percentuais e valores monetários
    6. Priorize ações por URGÊNCIA (Crítico > Alto > Médio > Baixo)
    7. Mencione impacto financeiro das recomendações
    8. Se dados insuficientes, seja claro sobre limitações
    
    FORMATO DE RESPOSTA:
    - Seja DIRETO e OBJETIVO
    - Use bullet points para ações
    - Inclua NÚMEROS e DADOS concretos
    - Destaque URGÊNCIAS com emojis (🚨 Crítico, ⚠️ Atenção, ✅ OK)
    - Termine com próximos passos claros
    - Use Markdown para formatação
    
    EXEMPLOS DE ANÁLISES ASSERTIVAS:
    
    ❌ RUIM: "O produto X está com estoque baixo"
    ✅ BOM: "🚨 CRÍTICO: Produto X tem apenas 5 unidades (3 dias de cobertura). Demanda média: 1.7/dia. Sugestão: Comprar 25 unidades HOJE para 15 dias de cobertura."
    
    ❌ RUIM: "Alguns produtos vendem bem"
    ✅ BOM: "📈 TOP 3 Alta Rotatividade: Produto A (45 vendas/mês, R$ 2.340 receita), Produto B (38 vendas/mês, R$ 1.890), Produto C (32 vendas/mês, R$ 1.280). Mantenha estoque alto destes."
    
    RESPONDA DE FORMA ASSERTIVA E ACIONÁVEL:
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

def extract_products_from_invoice_image(image_bytes: bytes) -> str:
    """
    Usa o Gemini Pro Vision para extrair uma lista de produtos de uma imagem de nota fiscal.
    """
    if not model:
        raise Exception("Modelo de IA não inicializado.")

    image_part = {"mime_type": "image/jpeg", "data": image_bytes}
    
    prompt = """
    Analise a imagem desta Nota Fiscal (DANFE) e extraia APENAS a tabela de produtos.
    Sua resposta deve ser um JSON contendo uma lista de objetos.
    Cada objeto deve ter as chaves "descricao" e "quantidade".
    Ignore impostos, totais e outras informações. Foque apenas na lista de itens.
    Se um produto não tiver um código óbvio, use o nome/descrição como identificador.
    Exemplo de resposta: [{"descricao": "LUVA NITRILICA PRETA SEM PO TALGE CX 100UN.G", "quantidade": 60.0}, {"descricao": "SABAO EM PO OMO", "quantidade": 10.0}]
    """
    
    try:
        response = model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        print(f"Erro na API Gemini Vision: {e}")
        raise