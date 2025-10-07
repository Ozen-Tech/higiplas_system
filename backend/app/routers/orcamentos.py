# /backend/app/routers/orcamentos.py - CORREÇÃO DE RESPOSTA E PDF

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

@router.post("/", response_model=schemas_orcamento.Orcamento, summary="Cria um novo orçamento")
def criar_novo_orcamento(
    orcamento_in: schemas_orcamento.OrcamentoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    # 1. Cria o orçamento
    db_orcamento = crud_orcamento.create_orcamento(db=db, orcamento_in=orcamento_in, vendedor_id=current_user.id)
    
    # ===== CORREÇÃO IMPORTANTE =====
    # 2. Busca novamente o orçamento recém-criado, mas agora com todos os dados
    #    necessários (cliente, usuario, itens) para que a resposta seja validada com sucesso.
    #    Isso garante que a resposta do POST seja igual à resposta do GET /me/.
    orcamento_completo = db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(models.Orcamento.id == db_orcamento.id).first()

    return orcamento_completo

@router.get("/me/", response_model=List[schemas_orcamento.Orcamento], summary="Lista os orçamentos do vendedor logado")
def listar_meus_orcamentos(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud_orcamento.get_orcamentos_by_vendedor(db=db, vendedor_id=current_user.id)

@router.get("/{orcamento_id}/pdf/", summary="Gera um PDF para um orçamento específico")
def gerar_orcamento_pdf(
    orcamento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    orcamento = db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(models.Orcamento.id == orcamento_id).first()

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

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
        pdf.cell(95, 7, item.produto.nome.encode('latin-1', 'replace').decode('latin-1'), 1) # Tratamento de caracteres
        pdf.cell(20, 7, str(item.quantidade), 1, 0, 'C')
        pdf.cell(35, 7, f'R$ {item.preco_unitario_congelado:.2f}', 1, 0, 'R')
        pdf.cell(35, 7, f'R$ {subtotal:.2f}', 1, 1, 'R')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, 'Valor Total do Orçamento:', 0, 0, 'R')
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 10, f'R$ {total_orcamento:.2f}', 1, 1, 'C', 1)

    # ===== CORREÇÃO IMPORTANTE DO PDF =====
    # A função .output('S') já retorna os bytes. Não precisa de .encode()
    pdf_bytes = pdf.output(dest='S')
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=orcamento_{orcamento.id}.pdf"}
    )