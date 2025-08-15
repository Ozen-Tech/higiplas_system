# /backend/app/routers/ai_pdf.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime

from ..services.pdf_processor import pdf_processor
from ..services.ai_service import generate_analysis_from_data
from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter()

class PDFProcessRequest(BaseModel):
    force_reprocess: bool = False

class AIQueryRequest(BaseModel):
    question: str
    include_pdf_data: bool = True

class MinimumStockRequest(BaseModel):
    product_name: str

class MinimumStockSuggestion(BaseModel):
    produto: str
    estoque_atual: Optional[int] = None
    estoque_minimo_sugerido: int
    justificativa: str
    aprovado: bool = False
    data_sugestao: str
    admin_aprovador: Optional[str] = None
    data_aprovacao: Optional[str] = None

@router.post("/process-pdfs")
async def process_sales_pdfs(
    request: PDFProcessRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Processa os PDFs de vendas e extrai dados históricos.
    Apenas administradores podem executar esta operação.
    """
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem processar PDFs"
        )
    
    try:
        # Verifica se já existem dados processados
        data_file = pdf_processor.backend_path / 'app' / 'dados_vendas_pdf_processados.json'
        
        if data_file.exists() and not request.force_reprocess:
            with open(data_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            return {
                "message": "Dados já processados. Use force_reprocess=true para reprocessar.",
                "data": existing_data['metadata'],
                "processed_at": existing_data['metadata']['processing_date']
            }
        
        # Processa os PDFs
        result = pdf_processor.process_all_pdfs()
        
        return {
            "message": "PDFs processados com sucesso",
            "data": result['summary'],
            "sales_records": len(result['sales_data'])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar PDFs: {str(e)}"
        )

@router.get("/top-selling-products")
async def get_top_selling_products(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Retorna os produtos mais vendidos baseado nos dados dos PDFs.
    """
    try:
        top_products = pdf_processor.get_top_selling_products(limit)
        
        if not top_products:
            return {
                "message": "Nenhum dado de vendas encontrado. Execute o processamento de PDFs primeiro.",
                "products": []
            }
        
        return {
            "message": f"Top {len(top_products)} produtos mais vendidos (Maio-Julho 2025)",
            "period": "2025-05-01 a 2025-07-31",
            "products": top_products
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar produtos mais vendidos: {str(e)}"
        )

@router.post("/ai-query")
async def query_ai_with_pdf_data(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Consulta a IA incluindo dados dos PDFs processados.
    """
    try:
        # Dados do sistema (pode ser expandido conforme necessário)
        system_data = f"Usuário: {current_user.nome} ({current_user.perfil})"
        
        pdf_data = None
        if request.include_pdf_data:
            # Carrega dados dos PDFs
            data_file = pdf_processor.backend_path / 'app' / 'dados_vendas_pdf_processados.json'
            
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    pdf_content = json.load(f)
                
                # Prepara resumo dos dados para a IA
                metadata = pdf_content['metadata']
                sales_data = pdf_content['sales_data']
                
                # Cria resumo dos produtos mais vendidos
                top_products = pdf_processor.get_top_selling_products(5)
                
                pdf_data = f"""
                RESUMO DOS DADOS DE VENDAS (MAIO-JULHO 2025):
                - Período: {metadata['period']}
                - Empresas: {', '.join(metadata['companies'])}
                - Total de registros de vendas: {metadata['total_sales_records']}
                - Arquivos processados: {metadata['files_processed']}
                
                TOP 5 PRODUTOS MAIS VENDIDOS:
                """
                
                for i, product in enumerate(top_products, 1):
                    pdf_data += f"""
                {i}. {product['produto']}
                   - Quantidade total vendida: {product['total_quantidade']}
                   - Valor total: R$ {product['total_valor']:.2f}
                   - Número de vendas: {product['numero_vendas']}
                """
        
        # Consulta a IA
        ai_response = generate_analysis_from_data(
            user_question=request.question,
            system_data=system_data,
            pdf_data=pdf_data
        )
        
        return {
            "question": request.question,
            "response": ai_response,
            "included_pdf_data": request.include_pdf_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar IA: {str(e)}"
        )

@router.post("/calculate-minimum-stock")
async def calculate_minimum_stock(
    request: MinimumStockRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calcula estoque mínimo para um produto baseado nos dados históricos.
    """
    try:
        result = pdf_processor.calculate_minimum_stock(request.product_name)
        
        if 'error' in result:
            raise HTTPException(
                status_code=404,
                detail=result['error']
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular estoque mínimo: {str(e)}"
        )

@router.post("/suggest-minimum-stocks")
async def suggest_minimum_stocks_for_top_products(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Gera sugestões de estoque mínimo para os produtos mais vendidos.
    Apenas administradores podem aprovar as sugestões.
    """
    try:
        top_products = pdf_processor.get_top_selling_products(limit)
        
        if not top_products:
            raise HTTPException(
                status_code=404,
                detail="Nenhum dado de produtos encontrado. Execute o processamento de PDFs primeiro."
            )
        
        suggestions = []
        
        for product in top_products:
            product_name = product['produto']
            stock_calc = pdf_processor.calculate_minimum_stock(product_name)
            
            if 'error' not in stock_calc:
                suggestion = MinimumStockSuggestion(
                    produto=product_name,
                    estoque_minimo_sugerido=stock_calc['estoque_minimo_sugerido'],
                    justificativa=f"Baseado em {stock_calc['total_vendido_periodo']} unidades vendidas no período. {stock_calc['criterio']}",
                    data_sugestao=datetime.now().isoformat()
                )
                suggestions.append(suggestion.dict())
        
        # Salva sugestões para aprovação posterior
        suggestions_file = pdf_processor.backend_path / 'app' / 'sugestoes_estoque_minimo.json'
        
        suggestions_data = {
            'generated_at': datetime.now().isoformat(),
            'generated_by': current_user.nome,
            'suggestions': suggestions
        }
        
        with open(suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions_data, f, ensure_ascii=False, indent=2)
        
        return {
            "message": f"Geradas {len(suggestions)} sugestões de estoque mínimo",
            "suggestions": suggestions,
            "requires_admin_approval": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar sugestões de estoque: {str(e)}"
        )

@router.get("/pending-stock-approvals")
async def get_pending_stock_approvals(
    current_user: User = Depends(get_current_user)
):
    """
    Lista sugestões de estoque mínimo pendentes de aprovação.
    Apenas administradores podem visualizar.
    """
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem visualizar aprovações pendentes"
        )
    
    try:
        suggestions_file = pdf_processor.backend_path / 'app' / 'sugestoes_estoque_minimo.json'
        
        if not suggestions_file.exists():
            return {
                "message": "Nenhuma sugestão de estoque encontrada",
                "suggestions": []
            }
        
        with open(suggestions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filtra apenas sugestões não aprovadas
        pending_suggestions = [
            suggestion for suggestion in data['suggestions']
            if not suggestion.get('aprovado', False)
        ]
        
        return {
            "message": f"{len(pending_suggestions)} sugestões pendentes de aprovação",
            "generated_at": data['generated_at'],
            "generated_by": data['generated_by'],
            "suggestions": pending_suggestions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar aprovações pendentes: {str(e)}"
        )

@router.post("/approve-stock-suggestion/{product_name}")
async def approve_stock_suggestion(
    product_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Aprova uma sugestão de estoque mínimo.
    Apenas administradores podem aprovar.
    """
    if current_user.perfil != "admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem aprovar sugestões de estoque"
        )
    
    try:
        suggestions_file = pdf_processor.backend_path / 'app' / 'sugestoes_estoque_minimo.json'
        
        if not suggestions_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Nenhuma sugestão de estoque encontrada"
            )
        
        with open(suggestions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Encontra e aprova a sugestão
        suggestion_found = False
        for suggestion in data['suggestions']:
            if suggestion['produto'].lower() == product_name.lower():
                suggestion['aprovado'] = True
                suggestion['admin_aprovador'] = current_user.nome
                suggestion['data_aprovacao'] = datetime.now().isoformat()
                suggestion_found = True
                break
        
        if not suggestion_found:
            raise HTTPException(
                status_code=404,
                detail=f"Sugestão para o produto '{product_name}' não encontrada"
            )
        
        # Salva as alterações
        with open(suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "message": f"Sugestão de estoque para '{product_name}' aprovada com sucesso",
            "approved_by": current_user.nome,
            "approved_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao aprovar sugestão: {str(e)}"
        )