from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from io import BytesIO
from datetime import datetime
import os

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..crud import ordem_compra as crud_oc
from ..schemas import ordem_compra as schemas_oc
from fpdf import FPDF

router = APIRouter(prefix="/ordens-compra", tags=["Ordens de Compra"])

@router.post("/", response_model=schemas_oc.OrdemDeCompra, status_code=201)
def create_new_ordem_compra(ordem: schemas_oc.OrdemDeCompraCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.create_ordem_compra(db=db, ordem_in=ordem, usuario_id=current_user.id)

@router.get("/", response_model=List[schemas_oc.OrdemDeCompra])
def read_ordens_compra(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.get_ordens_compra(db=db, empresa_id=current_user.empresa_id)

@router.get("/{ordem_id}", response_model=schemas_oc.OrdemDeCompra)
def get_ordem_compra(ordem_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.get_ordem_compra_by_id(db=db, ordem_id=ordem_id, empresa_id=current_user.empresa_id)

@router.put("/{ordem_id}", response_model=schemas_oc.OrdemDeCompra)
def update_ordem_compra(ordem_id: int, ordem_update: schemas_oc.OrdemDeCompraUpdate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.update_ordem_compra(db=db, ordem_id=ordem_id, ordem_update=ordem_update, empresa_id=current_user.empresa_id)

@router.delete("/{ordem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ordem_compra(ordem_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    crud_oc.delete_ordem_compra(db=db, ordem_id=ordem_id, empresa_id=current_user.empresa_id)
    from fastapi import Response
    return Response(status_code=status.HTTP_204_NO_CONTENT)

class OrdemCompraPDF(FPDF):
    """Classe personalizada para gerar PDFs profissionais de ordens de compra"""
    
    def __init__(self, ordem_data):
        super().__init__()
        self.ordem_data = ordem_data
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Cabeçalho profissional com logo e informações da empresa"""
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'HIGIPLAS-LOGO-2048x761.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 60)

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

        self.set_y(40)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, 40, 200, 40)
        self.ln(5)
    
    def footer(self):
        """Rodapé profissional"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        self.cell(0, 10, f'Ordem de Compra #{self.ordem_data["id"]} - Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.set_text_color(0, 0, 0)
    
    def titulo_ordem(self):
        """Título da ordem"""
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, 'ORDEM DE COMPRA', 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 10)
        data_str = self.ordem_data.get('data_criacao', datetime.now().strftime("%d/%m/%Y"))
        if isinstance(data_str, str):
            try:
                data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                data_str = data_obj.strftime("%d/%m/%Y")
            except:
                pass
        self.cell(0, 6, f'Nº {self.ordem_data["id"]:05d} - {data_str}', 0, 1, 'C')
        self.ln(5)
    
    def secao_fornecedor(self):
        """Seção com informações do fornecedor"""
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'DADOS DO FORNECEDOR', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(245, 245, 245)
        self.rect(10, self.get_y(), 190, 20, 'F')
        y_start = self.get_y() + 3
        self.set_y(y_start)
        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Nome:', 0, 0)
        self.set_font('Arial', '', 9)
        fornecedor_nome = self.ordem_data.get('fornecedor_nome') or 'N/A'
        self.cell(0, 5, fornecedor_nome, 0, 1)
        self.ln(3)
    
    def tabela_produtos(self):
        """Tabela de produtos"""
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'PRODUTOS SOLICITADOS', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 9)
        self.cell(10, 8, 'Item', 1, 0, 'C', True)
        self.cell(100, 8, 'Produto', 1, 0, 'C', True)
        self.cell(30, 8, 'Quantidade', 1, 0, 'C', True)
        self.cell(30, 8, 'Custo Unit.', 1, 0, 'C', True)
        self.cell(20, 8, 'Subtotal', 1, 1, 'C', True)
        self.set_font('Arial', '', 9)
        total = 0
        for idx, item in enumerate(self.ordem_data.get('itens', []), 1):
            if idx % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(255, 255, 255)
            subtotal = item.get('quantidade_solicitada', 0) * item.get('custo_unitario_registrado', 0)
            total += subtotal
            produto_nome = item.get('produto_nome', 'N/A')[:45]
            self.cell(10, 7, str(idx), 1, 0, 'C', True)
            self.cell(100, 7, produto_nome, 1, 0, 'L', True)
            self.cell(30, 7, str(item.get('quantidade_solicitada', 0)), 1, 0, 'C', True)
            self.cell(30, 7, f'R$ {item.get("custo_unitario_registrado", 0):,.2f}', 1, 0, 'R', True)
            self.cell(20, 7, f'R$ {subtotal:,.2f}', 1, 1, 'R', True)
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.cell(170, 10, 'VALOR TOTAL', 1, 0, 'R', True)
        self.cell(20, 10, f'R$ {total:,.2f}', 1, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

@router.get("/{ordem_id}/pdf/", summary="Gera um PDF profissional para uma ordem de compra")
def gerar_ordem_pdf(
    ordem_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera um PDF profissional da ordem de compra"""
    ordem = crud_oc.get_ordem_compra_by_id(db, ordem_id, current_user.empresa_id)
    
    ordem_data = {
        'id': ordem.id,
        'data_criacao': ordem.data_criacao.isoformat() if ordem.data_criacao else datetime.now().isoformat(),
        'fornecedor_nome': ordem.fornecedor.nome if ordem.fornecedor else 'N/A',
        'status': ordem.status,
        'itens': [
            {
                'produto_nome': item.produto.nome if item.produto else 'N/A',
                'quantidade_solicitada': item.quantidade_solicitada,
                'custo_unitario_registrado': item.custo_unitario_registrado,
            }
            for item in ordem.itens
        ]
    }

    pdf = OrdemCompraPDF(ordem_data)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.titulo_ordem()
    pdf.secao_fornecedor()
    pdf.tabela_produtos()

    pdf_bytes = pdf.output(dest='S')
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ordem_compra_{ordem.id:05d}.pdf"}
    )

@router.put("/{ordem_id}/receber", response_model=schemas_oc.OrdemDeCompra)
def receive_ordem_compra(ordem_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.receber_ordem_compra(db=db, ordem_id=ordem_id, usuario_id=current_user.id, empresa_id=current_user.empresa_id)