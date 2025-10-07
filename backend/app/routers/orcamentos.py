# /backend/app/routers/orcamentos.py - CORREÇÃO FINAL

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from io import BytesIO

from app.db.connection import get_db
from app.dependencies import get_current_user
from app.db import models
from app.schemas import orcamento as schemas_orcamento
from app.crud import orcamento as crud_orcamento
from fpdf import FPDF

router = APIRouter(
    prefix="/orcamentos",
    tags=["Orçamentos"]
)

# Rota para criar (sem alterações)
@router.post("/", response_model=schemas_orcamento.Orcamento, summary="Cria um novo orçamento")
def criar_novo_orcamento(
    orcamento_in: schemas_orcamento.OrcamentoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud_orcamento.create_orcamento(db=db, orcamento_in=orcamento_in, vendedor_id=current_user.id)

# Rota para histórico (sem alterações)
@router.get("/me/", response_model=List[schemas_orcamento.Orcamento], summary="Lista os orçamentos do vendedor logado")
def listar_meus_orcamentos(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud_orcamento.get_orcamentos_by_vendedor(db=db, vendedor_id=current_user.id)

# Rota de PDF
@router.get("/{orcamento_id}/pdf/", summary="Gera um PDF para um orçamento específico")
def gerar_orcamento_pdf(
    orcamento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    # CORREÇÃO: Adicionado o joinedload para o 'usuario' também aqui
    orcamento = db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario), # <<< LINHA ADICIONADA
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(models.Orcamento.id == orcamento_id).first()

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    # ... Lógica de criação do PDF (sem alterações)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Orçamento de Venda', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f'Cliente: {orcamento.cliente.razao_social}', 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, f'Telefone: {orcamento.cliente.telefone}', 0, 1)
    pdf.cell(0, 5, f'Data: {orcamento.data_criacao.strftime("%d/%m/%Y")}', 0, 1)
    pdf.cell(0, 5, f'Vendedor: {orcamento.usuario.nome}', 0, 1)
    pdf.cell(0, 5, f'Cond. Pagamento: {orcamento.condicao_pagamento}', 0, 1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 8, 'Produto', 1, 0, 'C')
    pdf.cell(20, 8, 'Qtd', 1, 0, 'C')
    pdf.cell(35, 8, 'Preco Unit.', 1, 0, 'C')
    pdf.cell(35, 8, 'Subtotal', 1, 1, 'C')
    pdf.set_font("Arial", '', 9)
    total_orcamento = 0
    for item in orcamento.itens:
        subtotal = item.quantidade * item.preco_unitario_congelado
        total_orcamento += subtotal
        pdf.cell(95, 7, item.produto.nome, 1)
        pdf.cell(20, 7, str(item.quantidade), 1, 0, 'C')
        pdf.cell(35, 7, f'R$ {item.preco_unitario_congelado:.2f}', 1, 0, 'R')
        pdf.cell(35, 7, f'R$ {subtotal:.2f}', 1, 1, 'R')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, 'Valor Total do Orçamento:', 0, 0, 'R')
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 10, f'R$ {total_orcamento:.2f}', 1, 1, 'C', 1)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=orcamento_{orcamento.id}.pdf"}
    )