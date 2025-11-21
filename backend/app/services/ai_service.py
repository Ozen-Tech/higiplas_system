# /backend/app/services/ai_service.py

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import json
import os
from pathlib import Path

# Inicializa a variável do modelo
model = None

# Tenta configurar a API ao iniciar o módulo
try:
    # Configura a API com a chave
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    # Configuração de segurança para permitir respostas menos restritivas
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    # Usa o modelo mais recente disponível (gemini-2.0-flash ou gemini-1.5-pro)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety_settings)
        print("✅ Modelo de IA Gemini 2.0 Flash inicializado com sucesso.")
    except Exception:
        # Fallback para modelo anterior se o 2.0 não estiver disponível
        model = genai.GenerativeModel('gemini-1.5-pro', safety_settings=safety_settings)
        print("✅ Modelo de IA Gemini 1.5 Pro inicializado com sucesso.")

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
    Usa Gemini como analista inteligente de estoque.
    """
    if not model:
        raise Exception("Erro: O modelo de IA não foi inicializado corretamente. Verifique a chave da API e a configuração do serviço no servidor.")
    
    # Carrega dados históricos de vendas automaticamente
    historical_data = load_historical_sales_data()
    
    # Mega prompt para análise assertiva de dados - Analista Inteligente Completo
    prompt_template = f"""Você é a "Rozana", ANALISTA INTELIGENTE COMPLETO da Higiplas.

MISSÃO: Fornecer análises ASSERTIVAS, PRECISAS e ACIONÁVEIS baseadas em TODOS os dados reais da empresa.

PERGUNTA DO GESTOR: "{user_question}"

═══════════════════════════════════════════════════════════════
DADOS COMPLETOS DO SISTEMA DISPONÍVEIS PARA ANÁLISE:
═══════════════════════════════════════════════════════════════

{system_data}

═══════════════════════════════════════════════════════════════
DADOS HISTÓRICOS DE VENDAS:
═══════════════════════════════════════════════════════════════

{historical_data}

═══════════════════════════════════════════════════════════════
DADOS ADICIONAIS DOS PDFs (MAIO-JULHO 2025):
═══════════════════════════════════════════════════════════════

{pdf_data if pdf_data else 'Dados adicionais dos PDFs não disponíveis'}

═══════════════════════════════════════════════════════════════
AUTONOMIA TOTAL DE ANÁLISE:
═══════════════════════════════════════════════════════════════

Você tem acesso COMPLETO a todos os dados do sistema e pode analisar QUALQUER informação disponível:

📦 ESTOQUE E PRODUTOS:
✅ Estoque atual de todos os produtos (quantidade, mínimo, preços, categorias)
✅ Histórico completo de movimentações (entradas/saídas)
✅ Produtos críticos, com baixo estoque ou sem movimento
✅ Análise de rotatividade e giro de estoque
✅ Cálculo de estoque mínimo baseado em demanda
✅ Sugestões de compra e reposição

💰 VENDAS E FINANCEIRO:
✅ Histórico completo de vendas e produtos mais vendidos
✅ Análise de receita, lucro e margens por produto
✅ Orçamentos recentes e status
✅ Análise de performance de vendas

👥 CLIENTES E RELACIONAMENTOS:
✅ Base completa de clientes cadastrados
✅ Status de pagamento e histórico
✅ Localização e segmentação de clientes
✅ Análise de relacionamento com clientes

📋 OPERAÇÕES:
✅ Ordens de compra recentes e status
✅ Fornecedores cadastrados
✅ Fluxo de compras e recebimentos
✅ Análise de processos operacionais

📊 ESTATÍSTICAS E KPIs:
✅ Estatísticas gerais de movimentações
✅ Indicadores de performance
✅ Tendências e padrões temporais
✅ Análise comparativa de períodos
✅ Resumo de vendas confirmadas via notas fiscais eletrônicas (dados em `resumo_vendas_nf_confirmadas`)
✅ Resumo de vendas confirmadas pelos vendedores/operadores (dados em `resumo_vendas_vendedores_confirmadas`)

CAPACIDADES DE ANÁLISE:
✅ Analisar QUALQUER aspecto do negócio usando os dados disponíveis
✅ Cruzar informações de diferentes módulos para insights completos
✅ Identificar padrões, tendências e anomalias
✅ Fazer recomendações estratégicas baseadas em dados
✅ Calcular métricas, projeções e cenários
✅ Sugerir melhorias operacionais e estratégicas
✅ Analisar performance financeira e operacional
✅ Identificar oportunidades de crescimento
✅ Detectar riscos e problemas potenciais

INSTRUÇÕES PARA ANÁLISE INTELIGENTE E AUTÔNOMA:

1. AUTONOMIA TOTAL: Use QUALQUER dado disponível no sistema para responder a pergunta
2. CRUZAMENTO DE DADOS: Sempre cruze informações de diferentes módulos (estoque + vendas + clientes + compras)
3. ANÁLISE PROFUNDA: Não se limite apenas ao óbvio - explore correlações e insights ocultos
4. CONTEXTUALIZAÇÃO: Relacione a pergunta com o contexto completo do negócio
5. FÓRMULAS E CÁLCULOS:
   - Estoque Mínimo = (Demanda Média Diária × Lead Time) × Margem de Segurança (1.2)
   - Dias de Cobertura = estoque_atual / demanda_media_diaria
   - Giro de Estoque = vendas_periodo / estoque_medio
   - Margem de Lucro = (preco_venda - preco_custo) / preco_venda × 100
6. SEMPRE inclua números concretos, percentuais e valores monetários
7. Priorize ações por URGÊNCIA e IMPACTO (Crítico > Alto > Médio > Baixo)
8. Mencione impacto financeiro e operacional das recomendações
9. Se dados insuficientes, seja claro sobre limitações mas sugira como obter mais dados
10. Analise padrões temporais, sazonalidade e tendências
11. IDENTIFIQUE OPORTUNIDADES: Além de problemas, sugira oportunidades de melhoria
12. VISÃO ESTRATÉGICA: Pense além do operacional - considere impacto no negócio como um todo
13. Ao falar de vendas confirmadas:
    - Utilize apenas os registros presentes nos arrays `resumo_vendas_nf_confirmadas` (saídas importadas de NF) e `resumo_vendas_vendedores_confirmadas` (vendas via aplicativo de vendedores).
    - Ignore completamente movimentações com observações vazias ou contendo “entrada manual”/“saída manual”.
    - Informe claramente qual fonte de dados foi usada (NF ou Vendedores) quando citar números.

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
        print("[AI Service] Gerando análise com Gemini...")
        response = model.generate_content(prompt_template)
        
        # Bloco de tratamento de erro para respostas bloqueadas
        try:
            print("[AI Service] Resposta da IA recebida.")
            return response.text
        except ValueError:
            print(f"❌ Resposta da IA bloqueada. Feedback do prompt: {response.prompt_feedback}")
            return f"A resposta da IA foi bloqueada por razões de segurança. Verifique a pergunta ou os dados enviados. Motivo do bloqueio: {response.prompt_feedback}"

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
    Usa o Gemini para extrair uma lista de produtos de uma imagem de nota fiscal.
    """
    if not model:
        raise Exception("Modelo de IA não inicializado.")

    prompt = """
    Analise a imagem desta Nota Fiscal (DANFE) e extraia APENAS a tabela de produtos.
    Sua resposta deve ser um JSON contendo uma lista de objetos.
    Cada objeto deve ter as chaves "descricao" e "quantidade".
    Ignore impostos, totais e outras informações. Foque apenas na lista de itens.
    Se um produto não tiver um código óbvio, use o nome/descrição como identificador.
    Exemplo de resposta: [{"descricao": "LUVA NITRILICA PRETA SEM PO TALGE CX 100UN.G", "quantidade": 60.0}, {"descricao": "SABAO EM PO OMO", "quantidade": 10.0}]
    """
    
    try:
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        print(f"Erro na API Gemini Vision: {e}")
        raise