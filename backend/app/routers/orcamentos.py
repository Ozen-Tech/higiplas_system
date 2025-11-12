# /backend/app/routers/orcamentos.py - CORREÇÃO DE RESPOSTA E PDF

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from io import BytesIO
from datetime import datetime
import os

from app.db.connection import get_db
from app.dependencies import get_current_user, get_admin_user
from app.db import models
from app.schemas import orcamento as schemas_orcamento
from app.crud import orcamento as crud_orcamento
from fpdf import FPDF

router = APIRouter(
    prefix="/orcamentos",
    tags=["Orçamentos"]
)

class OrcamentoPDF(FPDF):
    """Classe personalizada para gerar PDFs profissionais de orçamentos"""
    
    def __init__(self, orcamento_data):
        super().__init__()
        self.orcamento_data = orcamento_data
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
        self.line(10, 40, 200, 40)

        self.ln(5)
    
    def footer(self):
        """Rodapé profissional"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Linha separadora
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        
        # Texto do rodapé
        self.cell(0, 10, f'Orçamento #{self.orcamento_data["id"]} - Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        # Reset cor do texto
        self.set_text_color(0, 0, 0)
    
    def titulo_orcamento(self):
        """Título do orçamento"""
        self.set_font('Arial', 'B', 18)
        self.set_text_color(0, 102, 204)  # Azul
        self.cell(0, 10, 'ORÇAMENTO DE VENDA', 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        
        # Número do orçamento e data
        self.set_font('Arial', '', 10)
        self.cell(0, 6, f'Nº {self.orcamento_data["id"]:05d} - {self.orcamento_data["data"]}', 0, 1, 'C')
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
        self.rect(10, self.get_y(), 190, 25, 'F')

        y_start = self.get_y() + 3
        self.set_y(y_start)

        # Coluna esquerda
        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Nome:', 0, 0)
        self.set_font('Arial', '', 9)
        razao = self.orcamento_data['cliente'].get('razao_social') or 'N/A'
        self.cell(0, 5, razao, 0, 1)

        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'CNPJ/CPF:', 0, 0)
        self.set_font('Arial', '', 9)
        cnpj = self.orcamento_data['cliente'].get('cnpj') or 'N/A'
        self.cell(0, 5, cnpj, 0, 1)

        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Telefone:', 0, 0)
        self.set_font('Arial', '', 9)
        telefone = self.orcamento_data['cliente'].get('telefone') or 'N/A'
        self.cell(60, 5, telefone, 0, 0)

        self.set_font('Arial', 'B', 9)
        self.cell(30, 5, 'Email:', 0, 0)
        self.set_font('Arial', '', 9)
        email = self.orcamento_data['cliente'].get('email') or 'N/A'
        self.cell(0, 5, email, 0, 1)

        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Endereço:', 0, 0)
        self.set_font('Arial', '', 9)
        endereco = self.orcamento_data['cliente'].get('endereco') or 'N/A'
        self.multi_cell(0, 5, endereco)

        self.ln(3)
    
    def secao_vendedor(self):
        """Seção com informações do vendedor e condições"""
        # Título da seção
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'INFORMAÇÕES DO ORÇAMENTO', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        
        # Box com informações
        self.set_fill_color(245, 245, 245)
        self.rect(10, self.get_y(), 190, 15, 'F')
        
        y_start = self.get_y() + 3
        self.set_y(y_start)
        
        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Vendedor:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(60, 5, self.orcamento_data['vendedor'], 0, 0)
        
        self.set_font('Arial', 'B', 9)
        self.cell(40, 5, 'Condição de Pagamento:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(0, 5, self.orcamento_data['condicao_pagamento'], 0, 1)
        
        self.set_font('Arial', 'B', 9)
        self.set_x(12)
        self.cell(40, 5, 'Validade:', 0, 0)
        self.set_font('Arial', '', 9)
        self.cell(0, 5, '30 dias', 0, 1)
        
        self.ln(5)
    
    def tabela_produtos(self):
        """Tabela de produtos com design profissional"""
        # Título da seção
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'PRODUTOS E SERVIÇOS', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        
        self.ln(2)
        
        # Cabeçalho da tabela
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 9)
        self.cell(10, 8, 'Item', 1, 0, 'C', True)
        self.cell(85, 8, 'Descrição do Produto', 1, 0, 'C', True)
        self.cell(20, 8, 'Qtd', 1, 0, 'C', True)
        self.cell(35, 8, 'Preço Unit.', 1, 0, 'C', True)
        self.cell(40, 8, 'Subtotal', 1, 1, 'C', True)
        
        # Linhas da tabela
        self.set_font('Arial', '', 9)
        total = 0
        
        for idx, item in enumerate(self.orcamento_data['itens'], 1):
            # Alternar cores das linhas
            if idx % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(255, 255, 255)
            
            subtotal = item['quantidade'] * item['preco_unitario']
            total += subtotal
            
            self.cell(10, 7, str(idx), 1, 0, 'C', True)
            self.cell(85, 7, item['produto_nome'][:45], 1, 0, 'L', True)
            self.cell(20, 7, str(item['quantidade']), 1, 0, 'C', True)
            self.cell(35, 7, f'R$ {item["preco_unitario"]:,.2f}', 1, 0, 'R', True)
            self.cell(40, 7, f'R$ {subtotal:,.2f}', 1, 1, 'R', True)
        
        # Total
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.cell(150, 10, 'VALOR TOTAL DO ORÇAMENTO', 1, 0, 'R', True)
        self.cell(40, 10, f'R$ {total:,.2f}', 1, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        
        self.ln(5)
    
    def secao_observacoes(self):
        """Seção de observações e termos"""
        # Resetar posição X para margem esquerda
        self.set_x(10)

        # Título da seção
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'OBSERVAÇÕES E TERMOS', 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)

        self.ln(2)

        # Observacoes
        self.set_font('Arial', '', 9)
        observacoes = [
            '- Este orcamento tem validade de 30 dias a partir da data de emissao.',
            '- Os precos estao sujeitos a alteracao sem aviso previo.',
            '- O prazo de entrega sera informado apos confirmacao do pedido.',
            '- Frete nao incluso no valor do orcamento.',
            '- Pagamento conforme condicao especificada acima.',
        ]

        for obs in observacoes:
            self.set_x(10)  # Resetar X antes de cada linha
            self.multi_cell(0, 5, obs)

        self.ln(5)

        # Assinatura
        self.set_font('Arial', 'I', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Agradecemos a preferencia e estamos a disposicao para esclarecimentos.', 0, 1, 'C')
        self.set_text_color(0, 0, 0)

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

@router.get("/{orcamento_id}/pdf/", summary="Gera um PDF profissional para um orçamento específico")
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

    # Preparar dados para o PDF
    orcamento_data = {
        'id': orcamento.id,
        'data': orcamento.data_criacao.strftime("%d/%m/%Y"),
        'cliente': {
            'razao_social': orcamento.cliente.razao_social,
            'cnpj': getattr(orcamento.cliente, 'cnpj', 'N/A'),
            'telefone': orcamento.cliente.telefone or 'N/A',
            'email': getattr(orcamento.cliente, 'email', 'N/A'),
            'endereco': getattr(orcamento.cliente, 'endereco', 'N/A'),
        },
        'vendedor': orcamento.usuario.nome,
        'condicao_pagamento': orcamento.condicao_pagamento,
        'itens': [
            {
                'produto_nome': item.produto.nome,
                'quantidade': item.quantidade,
                'preco_unitario': float(item.preco_unitario_congelado),
            }
            for item in orcamento.itens
        ]
    }

    # Criar PDF profissional
    pdf = OrcamentoPDF(orcamento_data)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Adicionar seções
    pdf.titulo_orcamento()
    pdf.secao_cliente()
    pdf.secao_vendedor()
    pdf.tabela_produtos()
    pdf.secao_observacoes()

    # Gerar bytes do PDF
    pdf_bytes = pdf.output(dest='S')
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=orcamento_{orcamento.id:05d}.pdf"}
    )

# ============= ROTAS ADMIN =============

@router.get("/admin/todos", response_model=List[schemas_orcamento.Orcamento], summary="Lista todos os orçamentos (apenas admin)")
def listar_todos_orcamentos(
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Lista todos os orçamentos do sistema. Apenas para administradores."""
    return crud_orcamento.get_all_orcamentos(db=db, empresa_id=admin_user.empresa_id)

@router.get("/{orcamento_id}", response_model=schemas_orcamento.Orcamento, summary="Busca um orçamento específico")
def buscar_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca um orçamento específico por ID."""
    orcamento = crud_orcamento.get_orcamento_by_id(db=db, orcamento_id=orcamento_id)
    
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    
    # ✅ Corrigido: valida se o usuário é admin ou gestor
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    is_vendedor_owner = orcamento.usuario_id == current_user.id

    if not (is_admin or is_vendedor_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este orçamento"
        )
    
    return orcamento

@router.put("/{orcamento_id}", response_model=schemas_orcamento.Orcamento, summary="Edita um orçamento (apenas admin)")
def editar_orcamento(
    orcamento_id: int,
    orcamento_update: schemas_orcamento.OrcamentoUpdate,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Edita um orçamento existente. Apenas para administradores."""
    return crud_orcamento.update_orcamento(
        db=db,
        orcamento_id=orcamento_id,
        orcamento_update=orcamento_update
    )

@router.patch("/{orcamento_id}/status", response_model=schemas_orcamento.Orcamento, summary="Atualiza o status de um orçamento")
def atualizar_status_orcamento(
    orcamento_id: int,
    status_update: schemas_orcamento.OrcamentoStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Atualiza o status de um orçamento. Apenas para administradores."""
    return crud_orcamento.update_orcamento_status(
        db=db,
        orcamento_id=orcamento_id,
        novo_status=status_update.status
    )

@router.post("/{orcamento_id}/confirmar", response_model=schemas_orcamento.Orcamento, summary="Confirma orçamento e dá baixa no estoque")
def confirmar_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """
    Confirma um orçamento e processa a baixa de estoque dos produtos.
    Apenas para administradores.
    """
    return crud_orcamento.confirmar_orcamento(
        db=db,
        orcamento_id=orcamento_id,
        usuario_id=admin_user.id,
        empresa_id=admin_user.empresa_id
    )
