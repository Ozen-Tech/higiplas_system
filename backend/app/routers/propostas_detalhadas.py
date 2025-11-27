# backend/app/routers/propostas_detalhadas.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from io import BytesIO
from datetime import datetime
import os

from app.db.connection import get_db
from app.dependencies import get_current_user, get_admin_user
from app.db import models
from app.schemas import proposta_detalhada as schemas
from app.crud import proposta_detalhada as crud_proposta
from fpdf import FPDF

router = APIRouter(
    prefix="/propostas-detalhadas",
    tags=["Propostas Detalhadas"]
)


class PropostaDetalhadaPDF(FPDF):
    """Classe personalizada para gerar PDFs profissionais de propostas detalhadas"""
    
    def __init__(self, proposta_data):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.proposta_data = proposta_data
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Cabeçalho profissional com logo e informações da empresa"""
        # Logo da empresa
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'HIGIPLAS-LOGO-2048x761.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 60)

        # Informações da empresa no canto direito
        self.set_font('Arial', 'B', 10)
        self.set_xy(130, 10)
        self.cell(70, 5, 'T M Penha', 0, 1, 'R')

        self.set_font('Arial', '', 8)
        self.set_x(130)
        self.cell(70, 4, 'CNPJ: 22.599.389/0001-76', 0, 1, 'R')
        self.set_x(130)
        self.cell(70, 4, 'Rua 59, Quadra 41, 1 - Bequimão', 0, 1, 'R')
        self.set_x(130)
        self.cell(70, 4, 'São Luís/MA - CEP: 65.062-100', 0, 1, 'R')
        self.set_x(130)
        self.cell(70, 4, 'Tel: +55 98 8911-8396', 0, 1, 'R')
        self.set_x(130)
        self.cell(70, 4, 'vendas01@higiplas.com.br', 0, 1, 'R')

        # Linha separadora
        self.set_y(40)
        self.set_draw_color(0, 102, 204)  # Azul
        self.set_line_width(0.5)
        self.line(10, 40, 287, 40)

        self.ln(5)
    
    def footer(self):
        """Rodapé profissional"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Linha separadora
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y() - 2, 287, self.get_y() - 2)
        
        # Texto do rodapé
        self.cell(0, 10, f'Proposta Detalhada #{self.proposta_data["id"]} - Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        # Reset cor do texto
        self.set_text_color(0, 0, 0)
    
    def titulo_proposta(self):
        """Título da proposta"""
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 102, 204)  # Azul
        self.cell(0, 10, 'PROPOSTA DETALHADA', 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        
        # Número da proposta e data
        self.set_font('Arial', '', 10)
        data_str = self.proposta_data.get('data_criacao', datetime.now().strftime("%d/%m/%Y"))
        if isinstance(data_str, str):
            try:
                data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                data_str = data_obj.strftime("%d/%m/%Y")
            except:
                pass
        self.cell(0, 6, f'Nº {self.proposta_data["id"]:05d} - {data_str}', 0, 1, 'C')
        self.ln(5)
    
    def secao_cliente(self):
        """Seção com informações do cliente"""
        # Título da seção
        self.set_fill_color(0, 102, 204)  # Azul
        self.set_text_color(255, 255, 255)  # Branco
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'DADOS DO CLIENTE', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)

        # Box com informações do cliente
        self.set_fill_color(245, 245, 245)  # Cinza claro
        self.rect(10, self.get_y(), 190, 20, 'F')

        y_start = self.get_y() + 3
        self.set_y(y_start)

        # Informações do cliente
        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Nome:', 0, 0)
        self.set_font('Arial', '', 9)
        cliente_nome = self.proposta_data.get('cliente_nome') or 'N/A'
        self.cell(0, 5, cliente_nome, 0, 1)

        self.ln(3)
    
    def secao_resumo(self):
        """Quadro com métricas gerais da proposta"""
        itens = self.proposta_data.get('itens', [])
        total_itens = len(itens)
        total_rendimento = self.proposta_data.get('total_rendimento', 0)
        custo_medio = self.proposta_data.get('custo_medio')
        vendedor = self.proposta_data.get('vendedor_nome') or 'N/A'

        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'RESUMO DA PROPOSTA', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)

        self.set_fill_color(245, 245, 245)
        self.rect(10, self.get_y(), 267, 30, 'F')
        self.set_y(self.get_y() + 4)

        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(65, 6, 'Produtos Higiplas incluídos:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(60, 6, f'{total_itens} item(ns)', 0, 0)

        self.set_font('Arial', 'B', 9)
        self.cell(65, 6, 'Rendimento total estimado:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(60, 6, f'{total_rendimento:,.2f} litros', 0, 1)

        self.set_x(12)
        self.set_font('Arial', 'B', 9)
        self.cell(65, 6, 'Custo médio final por litro:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(60, 6, 'R$ {:.2f}'.format(custo_medio) if custo_medio else 'N/A', 0, 0)

        self.set_font('Arial', 'B', 9)
        self.cell(65, 6, 'Consultor responsável:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(0, 6, vendedor, 0, 1)

        self.ln(5)

    def secao_tabela_produtos(self):
        """Tabela comparativa entre Higiplas e produtos do cliente"""
        itens = self.proposta_data.get('itens', [])
        if not itens:
            return

        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'COMPARATIVO DE PRODUTOS', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)

        colunas = [60, 30, 30, 60, 45, 30]
        headers = [
            'PRODUTO HIGIPLAS',
            'RENDIMENTO',
            'CUSTO/L',
            'CONCORRENTE DO CLIENTE',
            'RENDIMENTO',
            'CUSTO/L',
        ]

        self.set_font('Arial', 'B', 8)
        for largura, titulo in zip(colunas, headers):
            self.cell(largura, 7, titulo, 1, 0, 'C', True)
        self.ln()

        self.set_font('Arial', '', 8)
        for item in itens:
            produto_nome = item.get('produto_nome') or self.proposta_data.get('produto_nome') or 'Produto Higiplas'
            self.cell(colunas[0], 7, produto_nome[:40], 1)
            rendimento = item.get('rendimento_total_litros')
            self.cell(colunas[1], 7, f"{rendimento:,.2f} L" if rendimento else 'N/A', 1, 0, 'C')
            custo = item.get('custo_por_litro_final')
            self.cell(colunas[2], 7, f"R$ {custo:,.2f}" if custo else 'N/A', 1, 0, 'C')
            concorrente_nome = item.get('concorrente_nome_manual') or 'Não informado'
            self.cell(colunas[3], 7, concorrente_nome[:35], 1)
            conc_rendimento = item.get('concorrente_rendimento_manual')
            self.cell(colunas[4], 7, f"{conc_rendimento:,.2f} L" if conc_rendimento else 'N/A', 1, 0, 'C')
            conc_custo = item.get('concorrente_custo_por_litro_manual')
            self.cell(colunas[5], 7, f"R$ {conc_custo:,.2f}" if conc_custo else 'N/A', 1, 0, 'C')
            self.ln()

        self.ln(5)
    
    def secao_comparacao(self):
        """Seção de comparação com concorrentes"""
        comparacoes = self.proposta_data.get('comparacoes', [])
        if not comparacoes:
            return
        
        # Título da seção
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'COMPARAÇÃO COM CONCORRENTES', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        
        self.ln(2)
        
        # Cabeçalho da tabela
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 9)
        self.cell(60, 8, 'Concorrente', 1, 0, 'C', True)
        self.cell(40, 8, 'Preço/Litro', 1, 0, 'C', True)
        self.cell(40, 8, 'Economia', 1, 0, 'C', True)
        self.cell(50, 8, 'Economia %', 1, 1, 'C', True)
        
        # Linhas da tabela
        self.set_font('Arial', '', 9)
        for idx, comp in enumerate(comparacoes[:5], 1):  # Limitar a 5 comparações
            if idx % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(255, 255, 255)
            
            nome = comp.get('concorrente_nome', 'N/A')[:30]
            preco = comp.get('custo_por_litro_concorrente', 0)
            economia_valor = comp.get('economia_valor', 0)
            economia_pct = comp.get('economia_percentual', 0)
            
            self.cell(60, 7, nome, 1, 0, 'L', True)
            self.cell(40, 7, f'R$ {preco:,.2f}' if preco else 'N/A', 1, 0, 'R', True)
            self.cell(40, 7, f'R$ {economia_valor:,.2f}' if economia_valor else 'N/A', 1, 0, 'R', True)
            self.cell(50, 7, f'{economia_pct:.1f}%' if economia_pct else 'N/A', 1, 1, 'C', True)
        
        self.ln(5)

    def secao_concorrentes_personalizados(self):
        """Seção para exibir os concorrentes cadastrados manualmente"""
        comparacoes_personalizadas = self.proposta_data.get('concorrentes_personalizados', [])
        if not comparacoes_personalizadas:
            return

        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'CONCORRENTES INDICADOS PELO CLIENTE', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)

        self.set_font('Arial', '', 9)
        for comp in comparacoes_personalizadas:
            self.set_fill_color(245, 245, 245)
            self.rect(10, self.get_y(), 267, 12, 'F')
            self.set_y(self.get_y() + 2)
            self.set_x(12)
            self.cell(80, 6, comp.get('nome', 'Concorrente'), 0, 0)
            rendimento = comp.get('rendimento_litro')
            custo = comp.get('custo_por_litro')
            self.cell(80, 6, f"Rendimento: {rendimento:,.2f} L" if rendimento else "Rendimento: N/A", 0, 0)
            self.cell(60, 6, f"Custo/L: R$ {custo:,.2f}" if custo else "Custo/L: N/A", 0, 1)
            observacoes = comp.get('observacoes')
            if observacoes:
                self.set_x(12)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 5, f"Notas: {observacoes}", 0, 1)
                self.set_font('Arial', '', 9)
            self.ln(2)
    
    def secao_observacoes(self):
        """Seção de observações"""
        observacoes = self.proposta_data.get('observacoes')
        if not observacoes:
            return
        
        # Título da seção
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'OBSERVAÇÕES', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        
        self.ln(2)
        
        # Observações
        self.set_font('Arial', '', 9)
        self.set_x(10)
        self.multi_cell(0, 5, observacoes)
        
        self.ln(5)


def _proposta_to_response(proposta: models.PropostaDetalhada, comparacoes: Optional[List[schemas.ComparacaoConcorrente]] = None) -> schemas.PropostaDetalhadaResponse:
    """Converte um modelo PropostaDetalhada para PropostaDetalhadaResponse"""
    itens = [
        schemas.PropostaDetalhadaItem.model_validate(item)
        for item in (proposta.itens or [])
    ]
    comparacoes_personalizadas = [
        schemas.ComparacaoConcorrenteManual.model_validate(comp)
        for comp in (proposta.concorrentes_personalizados or [])
    ]

    return schemas.PropostaDetalhadaResponse(
        id=proposta.id,
        orcamento_id=proposta.orcamento_id,
        cliente_id=proposta.cliente_id,
        produto_id=proposta.produto_id,
        quantidade_produto=proposta.quantidade_produto,
        dilucao_aplicada=proposta.dilucao_aplicada,
        dilucao_numerador=proposta.dilucao_numerador,
        dilucao_denominador=proposta.dilucao_denominador,
        concorrente_id=proposta.concorrente_id,
        observacoes=proposta.observacoes,
        compartilhavel=proposta.compartilhavel,
        vendedor_id=proposta.vendedor_id,
        ficha_tecnica_id=proposta.ficha_tecnica_id,
        rendimento_total_litros=proposta.rendimento_total_litros,
        preco_produto=proposta.preco_produto,
        custo_por_litro_final=proposta.custo_por_litro_final,
        economia_vs_concorrente=proposta.economia_vs_concorrente,
        economia_percentual=proposta.economia_percentual,
        economia_valor=proposta.economia_valor,
        token_compartilhamento=proposta.token_compartilhamento,
        data_criacao=proposta.data_criacao,
        data_atualizacao=proposta.data_atualizacao,
        produto_nome=proposta.produto.nome if proposta.produto else None,
        cliente_nome=proposta.cliente.razao_social if proposta.cliente else None,
        vendedor_nome=proposta.vendedor.nome if proposta.vendedor else None,
        ficha_tecnica=schemas.FichaTecnica.model_validate(proposta.ficha_tecnica) if proposta.ficha_tecnica else None,
        concorrente=schemas.ProdutoConcorrente.model_validate(proposta.concorrente) if proposta.concorrente else None,
        comparacoes=comparacoes or [],
        itens=itens,
        comparacoes_personalizadas=comparacoes_personalizadas or None,
    )


@router.post("/", response_model=schemas.PropostaDetalhadaResponse, status_code=status.HTTP_201_CREATED, summary="Cria proposta detalhada")
def create_proposta_detalhada(
    proposta_in: schemas.PropostaDetalhadaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Cria uma proposta detalhada com cálculos automáticos de rendimento e comparação com concorrentes.
    Disponível para vendedores.
    """
    from app.core.logger import app_logger
    item_log = proposta_in.itens[0] if proposta_in.itens else None
    app_logger.info(
        "Criando proposta detalhada para cliente %s com %s itens (primeiro produto=%s) pelo vendedor %s",
        proposta_in.cliente_id,
        len(proposta_in.itens),
        item_log.produto_id if item_log else proposta_in.produto_id,
        current_user.id,
    )
    try:
        proposta = crud_proposta.create_proposta_detalhada(
            db, proposta_in, current_user.id
        )
        app_logger.info(f"Proposta criada com sucesso: ID {proposta.id}")
        
        # Buscar proposta completa com relacionamentos
        proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
        
        if not proposta_completa:
            app_logger.error(f"Erro: Proposta {proposta.id} não encontrada após criação")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao recuperar proposta criada"
            )
        
        # Buscar comparações
        if proposta_completa.rendimento_total_litros and proposta_completa.custo_por_litro_final:
            comparacoes = crud_proposta.comparar_com_concorrentes(
                db,
                proposta_completa.produto_id,
                proposta_completa.rendimento_total_litros,
                proposta_completa.custo_por_litro_final,
                proposta_completa.produto.categoria if proposta_completa.produto else None
            )
        else:
            comparacoes = []
        
        # Montar resposta usando função auxiliar
        response = _proposta_to_response(proposta_completa, comparacoes)
        app_logger.info(f"Resposta montada com sucesso para proposta {proposta.id}")
        return response
        
    except ValueError as e:
        app_logger.error(f"Erro de validação ao criar proposta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Erro inesperado ao criar proposta: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar proposta: {str(e)}"
        )


@router.get("/me", response_model=List[schemas.PropostaDetalhadaResponse], summary="Lista minhas propostas")
def get_my_propostas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as propostas criadas pelo vendedor logado"""
    propostas = crud_proposta.get_propostas_by_vendedor(
        db, current_user.id, skip=skip, limit=limit
    )
    
    # Converter para response
    response_list = []
    for proposta in propostas:
        # Carregar relacionamentos se necessário
        if not proposta.produto:
            proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
            if proposta_completa:
                proposta = proposta_completa
        response_list.append(_proposta_to_response(proposta))
    
    return response_list


@router.get("/{proposta_id}", response_model=schemas.PropostaDetalhadaCompleta, summary="Visualiza proposta completa")
def get_proposta_by_id(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Visualiza uma proposta detalhada completa"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id, incluir_relacionamentos=True)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão: vendedor só vê suas próprias propostas, admin vê todas
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar esta proposta"
        )
    
    # Buscar comparações
    comparacoes = []
    if proposta.rendimento_total_litros and proposta.custo_por_litro_final:
        comparacoes = crud_proposta.comparar_com_concorrentes(
            db,
            proposta.produto_id,
            proposta.rendimento_total_litros,
            proposta.custo_por_litro_final,
            proposta.produto.categoria if proposta.produto else None
        )
    
    # Montar resposta usando função auxiliar e converter para Completa
    response = _proposta_to_response(proposta, comparacoes)
    return schemas.PropostaDetalhadaCompleta(**response.model_dump())


@router.get("/cliente/{cliente_id}", response_model=List[schemas.PropostaDetalhadaResponse], summary="Lista propostas de um cliente")
def get_propostas_by_cliente(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as propostas de um cliente específico"""
    propostas = crud_proposta.get_propostas_by_cliente(
        db, cliente_id, skip=skip, limit=limit
    )
    
    # Verificar permissão: vendedor só vê propostas de clientes que ele atende
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin:
        # Filtrar apenas propostas do vendedor
        propostas = [p for p in propostas if p.vendedor_id == current_user.id]
    
    response_list = []
    for proposta in propostas:
        # Carregar relacionamentos se necessário
        if not proposta.produto:
            proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
            if proposta_completa:
                proposta = proposta_completa
        response_list.append(_proposta_to_response(proposta))
    
    return response_list


@router.get("/admin/todas", response_model=List[schemas.PropostaDetalhadaResponse], summary="Lista todas as propostas (Admin)")
def get_all_propostas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Lista todas as propostas do sistema. Apenas para administradores."""
    propostas = crud_proposta.get_all_propostas(db, skip=skip, limit=limit)
    
    response_list = []
    for proposta in propostas:
        # Carregar relacionamentos se necessário
        if not proposta.produto:
            proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
            if proposta_completa:
                proposta = proposta_completa
        response_list.append(_proposta_to_response(proposta))
    
    return response_list


@router.post("/{proposta_id}/compartilhar", response_model=schemas.PropostaDetalhadaResponse, summary="Gera link compartilhável")
def compartilhar_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera token de compartilhamento para uma proposta"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para compartilhar esta proposta"
        )
    
    # Atualizar proposta para ser compartilhável
    import secrets
    proposta.compartilhavel = True
    proposta.token_compartilhamento = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(proposta)
    
    # Carregar relacionamentos
    proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
    if proposta_completa:
        proposta = proposta_completa
    
    return _proposta_to_response(proposta)


@router.get("/compartilhar/{token}", response_model=schemas.PropostaDetalhadaCompleta, summary="Visualiza proposta compartilhada")
def get_proposta_compartilhada(
    token: str,
    db: Session = Depends(get_db)
):
    """Visualiza uma proposta através do token de compartilhamento (público)"""
    proposta = crud_proposta.get_proposta_by_token(db, token)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada ou link inválido"
        )
    
    # Buscar comparações
    comparacoes = []
    if proposta.rendimento_total_litros and proposta.custo_por_litro_final:
        comparacoes = crud_proposta.comparar_com_concorrentes(
            db,
            proposta.produto_id,
            proposta.rendimento_total_litros,
            proposta.custo_por_litro_final,
            proposta.produto.categoria if proposta.produto else None
        )
    
    # Montar resposta usando função auxiliar e converter para Completa
    response = _proposta_to_response(proposta, comparacoes)
    return schemas.PropostaDetalhadaCompleta(**response.model_dump())


@router.put("/{proposta_id}", response_model=schemas.PropostaDetalhadaResponse, summary="Atualiza proposta")
def update_proposta(
    proposta_id: int,
    proposta_update: schemas.PropostaDetalhadaUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma proposta detalhada"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar esta proposta"
        )
    
    proposta_atualizada = crud_proposta.update_proposta_detalhada(
        db, proposta_id, proposta_update
    )
    
    if not proposta_atualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Erro ao atualizar proposta {proposta_id}"
        )
    
    proposta_completa = crud_proposta.get_proposta_by_id(db, proposta_id, incluir_relacionamentos=True)
    
    if not proposta_completa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Erro ao atualizar proposta {proposta_id}"
        )
    
    return _proposta_to_response(proposta_completa)


@router.get("/{proposta_id}/pdf/", summary="Gera um PDF profissional para uma proposta detalhada")
def gerar_proposta_pdf(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera um PDF profissional da proposta detalhada"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id, incluir_relacionamentos=True)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão: vendedor só vê suas próprias propostas, admin vê todas
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar esta proposta"
        )
    
    # Buscar comparações
    comparacoes = []
    if proposta.rendimento_total_litros and proposta.custo_por_litro_final:
        comparacoes = crud_proposta.comparar_com_concorrentes(
            db,
            proposta.produto_id,
            proposta.rendimento_total_litros,
            proposta.custo_por_litro_final,
            proposta.produto.categoria if proposta.produto else None
        )
    
    # Preparar dados para o PDF
    itens_data = [
        {
            'produto_nome': item.produto.nome if item.produto else None,
            'rendimento_total_litros': item.rendimento_total_litros,
            'custo_por_litro_final': item.custo_por_litro_final,
            'dilucao_aplicada': item.dilucao_aplicada,
            'concorrente_nome_manual': item.concorrente_nome_manual,
            'concorrente_rendimento_manual': item.concorrente_rendimento_manual,
            'concorrente_custo_por_litro_manual': item.concorrente_custo_por_litro_manual,
        }
        for item in proposta.itens
    ]
    total_rendimento = sum(item.get('rendimento_total_litros') or 0 for item in itens_data)
    custos_validos = [item.get('custo_por_litro_final') for item in itens_data if item.get('custo_por_litro_final')]
    custo_medio = sum(custos_validos) / len(custos_validos) if custos_validos else None

    proposta_data = {
        'id': proposta.id,
        'data_criacao': proposta.data_criacao.isoformat() if proposta.data_criacao else datetime.now().isoformat(),
        'cliente_nome': proposta.cliente.razao_social if proposta.cliente else 'N/A',
        'produto_nome': proposta.produto.nome if proposta.produto else 'N/A',
        'quantidade_produto': proposta.quantidade_produto,
        'dilucao_aplicada': proposta.dilucao_aplicada or 'N/A',
        'preco_produto': proposta.preco_produto or 0,
        'vendedor_nome': proposta.vendedor.nome if proposta.vendedor else 'N/A',
        'rendimento_total_litros': proposta.rendimento_total_litros or 0,
        'custo_por_litro_final': proposta.custo_por_litro_final or 0,
        'economia_percentual': proposta.economia_percentual,
        'economia_valor': proposta.economia_valor,
        'observacoes': proposta.observacoes,
        'itens': itens_data,
        'total_rendimento': total_rendimento,
        'custo_medio': custo_medio,
        'concorrentes_personalizados': [
            {
                'nome': comp.nome,
                'rendimento_litro': comp.rendimento_litro,
                'custo_por_litro': comp.custo_por_litro,
                'observacoes': comp.observacoes,
            }
            for comp in proposta.concorrentes_personalizados
        ],
        'comparacoes': [
            {
                'concorrente_nome': comp.concorrente_nome,
                'custo_por_litro_concorrente': comp.custo_por_litro_concorrente or 0,
                'economia_valor': comp.economia_valor or 0,
                'economia_percentual': comp.economia_percentual or 0,
            }
            for comp in comparacoes
        ]
    }

    # Criar PDF profissional
    pdf = PropostaDetalhadaPDF(proposta_data)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Adicionar seções
    pdf.titulo_proposta()
    pdf.secao_cliente()
    pdf.secao_resumo()
    pdf.secao_tabela_produtos()
    pdf.secao_concorrentes_personalizados()
    pdf.secao_comparacao()
    pdf.secao_observacoes()

    # Gerar bytes do PDF
    pdf_bytes = pdf.output(dest='S')
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=proposta_detalhada_{proposta.id:05d}.pdf"}
    )


@router.delete("/{proposta_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta proposta")
def delete_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta uma proposta detalhada"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar esta proposta"
        )
    
    sucesso = crud_proposta.delete_proposta_detalhada(db, proposta_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Erro ao deletar proposta {proposta_id}"
        )

