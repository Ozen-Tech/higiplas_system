# /backend/app/services/ai_service.py

from google import genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import json
import os
from pathlib import Path

# Inicializa o cliente da API
client = None

# Tenta configurar a API ao iniciar o módulo
try:
    # Inicializa o cliente com a chave da API
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    print("✅ Cliente de IA Gemini 3.0 inicializado com sucesso.")

except Exception as e:
    print(f"❌ Erro ao configurar a API do Gemini: {e}")

def load_historical_sales_data() -> str:
    """
    Carrega os dados históricos de vendas do arquivo JSON e formata para a IA.
    """
    try:
        # Caminho para o arquivo de dados históricos
        current_dir = Path(__file__).parent.parent
        data_file = current_dir / 'dados_historicos_vendas.json'
        
        if not data_file.exists():
            return "Dados históricos de vendas não encontrados."
        
        with open(data_file, 'r', encoding='utf-8') as f:
            historical_data = json.load(f)
        
        # Formata os dados para a IA
        formatted_data = "DADOS HISTÓRICOS DE VENDAS HIGIPLAS/HIGITEC:\n\n"
        
        # Pega os top 20 produtos mais vendidos por quantidade
        top_products = sorted(historical_data, key=lambda x: x['quantidade_vendida_total'], reverse=True)[:20]
        
        formatted_data += "TOP 20 PRODUTOS MAIS VENDIDOS (por quantidade):\n"
        for i, product in enumerate(top_products, 1):
            formatted_data += f"""{i}. {product['descricao']}
   - ID: {product['ident_antigo']}
   - Quantidade vendida: {product['quantidade_vendida_total']}
   - Valor total vendido: R$ {product['valor_vendido_total']:.2f}
   - Custo total: R$ {product['custo_compra_total']:.2f}
   - Lucro bruto: R$ {product['lucro_bruto_total']:.2f}
   - Margem de lucro: {product['margem_lucro_percentual']:.2f}%

"""
        
        # Adiciona estatísticas gerais
        total_products = len(historical_data)
        total_quantity = sum(p['quantidade_vendida_total'] for p in historical_data)
        total_revenue = sum(p['valor_vendido_total'] for p in historical_data)
        total_profit = sum(p['lucro_bruto_total'] for p in historical_data)
        
        formatted_data += f"""\nESTATÍSTICAS GERAIS:
- Total de produtos diferentes: {total_products}
- Quantidade total vendida: {total_quantity}
- Receita total: R$ {total_revenue:.2f}
- Lucro bruto total: R$ {total_profit:.2f}
- Margem média de lucro: {(total_profit/total_revenue*100):.2f}%

"""
        
        return formatted_data
        
    except Exception as e:
        print(f"Erro ao carregar dados históricos: {e}")
        return "Erro ao carregar dados históricos de vendas."

def generate_analysis_from_data(user_question: str, system_data: str, pdf_data: str = None) -> str:
    """
    Recebe uma pergunta do usuário e os dados do sistema, envia para a IA 
    com um prompt aprimorado e retorna a resposta.
    Usa Gemini 3.0 Pro Preview como analista inteligente de estoque.
    """
    if not client:
        raise Exception("Erro: O cliente de IA não foi inicializado corretamente. Verifique a chave da API e a configuração do serviço no servidor.")
    
    # Carrega dados históricos de vendas automaticamente
    historical_data = load_historical_sales_data()
    
    # Mega prompt para análise assertiva de dados - Analista Inteligente de Estoque
    prompt_template = f"""Você é a "Rozana", ANALISTA INTELIGENTE DE ESTOQUE da Higiplas.

MISSÃO: Fornecer análises ASSERTIVAS, PRECISAS e ACIONÁVEIS baseadas nos dados reais da empresa.

PERGUNTA DO GESTOR: "{user_question}"

DADOS DO SISTEMA (ESTOQUE ATUAL):
{system_data}

DADOS HISTÓRICOS DE VENDAS:
{historical_data}

DADOS ADICIONAIS DOS PDFs (MAIO-JULHO 2025):
{pdf_data if pdf_data else 'Dados adicionais dos PDFs não disponíveis'}

CAPACIDADES COMO ANALISTA DE ESTOQUE:
✅ Calcular estoque mínimo baseado em demanda histórica dos últimos 3 meses
✅ Analisar tendências de vendas por produto e empresa (HIGIPLAS/HIGITEC)
✅ Identificar produtos com maior rotatividade
✅ Sugerir estratégias de reposição de estoque
✅ Identificar produtos críticos que precisam de reposição URGENTE
✅ Analisar rotatividade e sazonalidade de produtos
✅ Detectar produtos parados que ocupam capital desnecessário
✅ Sugerir quantidades ideais de compra com base em lead time
✅ Prever rupturas de estoque antes que aconteçam
✅ Otimizar capital de giro através de análise de giro de estoque
✅ Analisar padrões de movimentação (entradas/saídas)
✅ Identificar produtos com estoque abaixo do mínimo
✅ Calcular dias de cobertura de estoque
✅ Sugerir ajustes de estoque mínimo baseado em histórico

INSTRUÇÕES PARA ANÁLISE INTELIGENTE:

1. SEMPRE cruze todos os datasets para análises completas
2. Para ESTOQUE MÍNIMO: Use fórmula = (Demanda Média Diária × Lead Time) × Margem de Segurança (1.2)
3. Para PRODUTOS CRÍTICOS: Identifique onde estoque_atual <= estoque_minimo OU estoque_atual < demanda_prevista_7_dias
4. Para SUGESTÕES DE COMPRA: Calcule quantidade = max(estoque_minimo_calculado - estoque_atual, demanda_prevista_15_dias - estoque_atual, 0)
5. Para DIAS DE COBERTURA: Calcule = estoque_atual / demanda_media_diaria
6. SEMPRE inclua números concretos, percentuais e valores monetários
7. Priorize ações por URGÊNCIA (Crítico > Alto > Médio > Baixo)
8. Mencione impacto financeiro das recomendações
9. Se dados insuficientes, seja claro sobre limitações
10. Analise padrões temporais (sazonalidade, tendências)

FORMATO DE RESPOSTA:
- Seja DIRETO e OBJETIVO
- Use bullet points para ações
- Inclua NÚMEROS e DADOS concretos
- Destaque URGÊNCIAS com emojis (🚨 Crítico, ⚠️ Atenção, ✅ OK)
- Termine com próximos passos claros
- Use Markdown para formatação
- Use tabelas quando apropriado

EXEMPLOS DE ANÁLISES ASSERTIVAS:

❌ RUIM: "O produto X está com estoque baixo"
✅ BOM: "🚨 CRÍTICO: Produto X tem apenas 5 unidades (3 dias de cobertura). Demanda média: 1.7/dia. Sugestão: Comprar 25 unidades HOJE para 15 dias de cobertura."

❌ RUIM: "Alguns produtos vendem bem"
✅ BOM: "📈 TOP 3 Alta Rotatividade: Produto A (45 vendas/mês, R$ 2.340 receita), Produto B (38 vendas/mês, R$ 1.890), Produto C (32 vendas/mês, R$ 1.280). Mantenha estoque alto destes."

RESPONDA DE FORMA ASSERTIVA E ACIONÁVEL COMO UM ANALISTA DE ESTOQUE EXPERIENTE:"""
     
    try:
        print("[AI Service] Gerando análise com Gemini 3.0 Pro Preview...")
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt_template
        )
        
        print("[AI Service] Resposta da IA recebida.")
        return response.text

    except Exception as e:
        error_message = str(e)
        print(f"❌ Erro na comunicação com a API do Gemini: {error_message}")
        
        # Detecta erro 429 (Rate Limit)
        if "429" in error_message or "Resource exhausted" in error_message or "quota" in error_message.lower():
            raise Exception("RATE_LIMIT_EXCEEDED: O limite de requisições da API foi excedido. Por favor, aguarde alguns minutos antes de tentar novamente.")
        
        # Detecta outros erros da API
        if "403" in error_message or "permission" in error_message.lower():
            raise Exception("API_PERMISSION_DENIED: Problema de permissão na API. Verifique a chave da API.")
        
        if "400" in error_message or "invalid" in error_message.lower():
            raise Exception("API_INVALID_REQUEST: Requisição inválida. O contexto pode estar muito grande.")
        
        # Outros erros
        raise Exception(f"API_ERROR: {error_message}")

def extract_products_from_invoice_image(image_bytes: bytes) -> str:
    """
    Usa o Gemini 3.0 Pro Preview para extrair uma lista de produtos de uma imagem de nota fiscal.
    """
    if not client:
        raise Exception("Cliente de IA não inicializado.")

    prompt = """
    Analise a imagem desta Nota Fiscal (DANFE) e extraia APENAS a tabela de produtos.
    Sua resposta deve ser um JSON contendo uma lista de objetos.
    Cada objeto deve ter as chaves "descricao" e "quantidade".
    Ignore impostos, totais e outras informações. Foque apenas na lista de itens.
    Se um produto não tiver um código óbvio, use o nome/descrição como identificador.
    Exemplo de resposta: [{"descricao": "LUVA NITRILICA PRETA SEM PO TALGE CX 100UN.G", "quantidade": 60.0}, {"descricao": "SABAO EM PO OMO", "quantidade": 10.0}]
    """
    
    try:
        # Para imagens, ainda precisamos usar a API antiga ou adaptar para a nova API
        # Por enquanto, vamos manter compatibilidade com a API antiga para visão
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=settings.GOOGLE_API_KEY)
        model_vision = genai_legacy.GenerativeModel('gemini-2.0-flash')
        
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = model_vision.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        print(f"Erro na API Gemini Vision: {e}")
        raise