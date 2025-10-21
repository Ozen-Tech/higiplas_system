# backend/app/routers/propostas.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
import os
from fpdf import FPDF

from app.dependencies import get_db, get_current_user
from app.db import models
from app.schemas import proposta as schemas_proposta
from app.crud import proposta as crud_proposta

router = APIRouter(
    prefix="/propostas",
    tags=["propostas"]
)

class PropostaPDF(FPDF):
    """Classe para gerar PDF profissional de propostas comerciais"""
    
    def __init__(self, proposta_data):
        super().__init__()
        self.proposta_data = proposta_data
        
    def header(self):
        """Cabeçalho do PDF com logo e informações da empresa"""
        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'HIGIPLAS-LOGO-2048x761.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 50)
        
        # Informações da empresa
        self.set_font('Arial', 'B', 10)
        self.set_xy(140, 10)
        self.cell(0, 5, 'HIGIPLAS INDUSTRIA E COMERCIO LTDA', 0, 1, 'R')
        
        self.set_font('Arial', '', 8)
        self.set_xy(140, 15)
        self.cell(0, 4, 'CNPJ: 00.000.000/0001-00', 0, 1, 'R')
        self.set_xy(140, 19)
        self.cell(0, 4, 'Fone: (00) 0000-0000', 0, 1, 'R')
        self.set_xy(140, 23)
        self.cell(0, 4, 'Email: contato@higiplas.com.br', 0, 1, 'R')
        
        # Linha separadora azul
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, 32, 200, 32)
        
        self.ln(25)
    
    def footer(self):
        """Rodapé do PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Proposta #{self.proposta_data["id"]} - Pagina {self.page_no()}', 0, 0, 'C')
    
    def titulo_proposta(self):
        """Título da proposta"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, 'PROPOSTA COMERCIAL', 0, 1, 'C')
        self.ln(5)
    
    def secao_cliente(self):
        """Seção com dados do cliente"""
        cliente = self.proposta_data.get('cliente', {})
        
        # Caixa cinza para dados do cliente
        self.set_fill_color(245, 245, 245)
        self.rect(10, self.get_y(), 190, 25, 'F')
        
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, 'DADOS DO CLIENTE', 0, 1)
        
        self.set_font('Arial', '', 10)
        
        # Nome/Razão Social
        nome = cliente.get('razao_social', 'N/A')
        self.cell(0, 5, f'Cliente: {nome}', 0, 1)
        
        # Telefone e Email na mesma linha
        telefone = cliente.get('telefone') or 'N/A'
        email = cliente.get('email') or 'N/A'
        self.cell(95, 5, f'Telefone: {telefone}', 0, 0)
        self.cell(95, 5, f'Email: {email}', 0, 1)
        
        # Endereço
        endereco = cliente.get('endereco') or 'N/A'
        self.cell(0, 5, f'Endereco: {endereco}', 0, 1)
        
        self.ln(5)
    
    def secao_vendedor(self):
        """Seção com informações do vendedor e da proposta"""
        vendedor = self.proposta_data.get('usuario', {})
        
        # Caixa cinza para informações da proposta
        self.set_fill_color(245, 245, 245)
        self.rect(10, self.get_y(), 190, 20, 'F')
        
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, 'INFORMACOES DA PROPOSTA', 0, 1)
        
        self.set_font('Arial', '', 10)
        
        # Vendedor e Data
        vendedor_nome = vendedor.get('nome', 'N/A')
        data_criacao = self.proposta_data.get('data_criacao', 'N/A')
        if data_criacao != 'N/A':
            # Formata a data
            try:
                from datetime import datetime
                if isinstance(data_criacao, str):
                    dt = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
                else:
                    dt = data_criacao
                data_criacao = dt.strftime('%d/%m/%Y')
            except:
                pass
        
        self.cell(95, 5, f'Vendedor: {vendedor_nome}', 0, 0)
        self.cell(95, 5, f'Data: {data_criacao}', 0, 1)
        
        # Status
        status = self.proposta_data.get('status', 'RASCUNHO')
        self.cell(0, 5, f'Status: {status}', 0, 1)
        
        self.ln(5)
    
    def tabela_produtos(self):
        """Tabela com os produtos da proposta"""
        itens = self.proposta_data.get('itens', [])
        
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 102, 204)
        self.cell(0, 8, 'PRODUTOS E SERVICOS', 0, 1)
        
        # Cabeçalho da tabela
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(0, 0, 0)
        
        self.cell(10, 7, 'ITEM', 1, 0, 'C', True)
        self.cell(50, 7, 'PRODUTO', 1, 0, 'C', True)
        self.cell(60, 7, 'DESCRICAO', 1, 0, 'C', True)
        self.cell(25, 7, 'VALOR', 1, 0, 'C', True)
        self.cell(25, 7, 'RENDIMENTO', 1, 0, 'C', True)
        self.cell(20, 7, 'R$/LITRO', 1, 1, 'C', True)
        
        # Itens da tabela
        self.set_font('Arial', '', 8)
        total_geral = 0
        
        for idx, item in enumerate(itens, 1):
            produto_nome = item.get('produto_nome', 'N/A')
            descricao = item.get('descricao', '')
            valor = item.get('valor', 0)
            rendimento = item.get('rendimento_litros', 'N/A')
            custo_litro = item.get('custo_por_litro', 0)
            
            total_geral += valor
            
            # Quebra de linha se necessário
            y_before = self.get_y()
            
            # Item
            self.cell(10, 6, str(idx), 1, 0, 'C')
            
            # Produto (com quebra de linha se necessário)
            x_produto = self.get_x()
            y_produto = self.get_y()
            self.multi_cell(50, 6, produto_nome, 1, 'L')
            y_after_produto = self.get_y()
            
            # Descrição
            self.set_xy(x_produto + 50, y_produto)
            self.multi_cell(60, 6, descricao[:100], 1, 'L')
            y_after_desc = self.get_y()
            
            # Ajusta altura da linha
            max_y = max(y_after_produto, y_after_desc)
            altura_linha = max_y - y_before
            
            # Valor
            self.set_xy(x_produto + 110, y_produto)
            self.cell(25, altura_linha, f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'), 1, 0, 'R')
            
            # Rendimento
            self.cell(25, altura_linha, str(rendimento), 1, 0, 'C')
            
            # Custo por litro
            if custo_litro and custo_litro > 0:
                custo_str = f'R$ {custo_litro:.2f}'.replace('.', ',')
            else:
                custo_str = '-'
            self.cell(20, altura_linha, custo_str, 1, 1, 'R')
        
        # Total
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.cell(145, 7, 'VALOR TOTAL DA PROPOSTA', 1, 0, 'R', True)
        self.cell(45, 7, f'R$ {total_geral:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'), 1, 1, 'R', True)
        
        self.ln(5)
    
    def secao_observacoes(self):
        """Seção de observações"""
        observacoes = self.proposta_data.get('observacoes', '')
        
        if observacoes:
            self.set_font('Arial', 'B', 11)
            self.set_text_color(0, 102, 204)
            self.cell(0, 8, 'OBSERVACOES', 0, 1)
            
            self.set_font('Arial', '', 9)
            self.set_text_color(0, 0, 0)
            self.multi_cell(0, 5, observacoes)
            self.ln(3)
        
        # Informações adicionais
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.multi_cell(0, 4, 
            'Esta proposta tem validade de 30 dias a partir da data de emissao.\n'
            'Os precos e condicoes estao sujeitos a alteracao sem aviso previo.\n'
            'Para mais informacoes, entre em contato conosco.'
        )

@router.post("/", response_model=schemas_proposta.Proposta, summary="Cria uma nova proposta")
def criar_nova_proposta(
    proposta_in: schemas_proposta.PropostaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova proposta comercial"""
    proposta = crud_proposta.create_proposta(db, proposta_in, current_user.id)
    
    # Recarrega a proposta com todos os relacionamentos
    proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, current_user.id)
    return proposta_completa

@router.get("/me/", response_model=List[schemas_proposta.Proposta], summary="Lista as propostas do vendedor logado")
def listar_minhas_propostas(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as propostas criadas pelo vendedor logado"""
    return crud_proposta.get_propostas_by_vendedor(db, current_user.id)

@router.get("/{proposta_id}/", response_model=schemas_proposta.Proposta, summary="Busca uma proposta específica")
def buscar_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca uma proposta específica por ID"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id, current_user.id)
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return proposta

@router.get("/{proposta_id}/pdf/", summary="Gera um PDF profissional para uma proposta específica")
def gerar_proposta_pdf(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera e retorna um PDF da proposta"""
    
    # Busca a proposta
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id, current_user.id)
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    
    # Prepara os dados para o PDF
    proposta_data = {
        'id': proposta.id,
        'status': proposta.status,
        'data_criacao': proposta.data_criacao,
        'observacoes': proposta.observacoes or '',
        'cliente': {
            'razao_social': proposta.cliente.razao_social if proposta.cliente else 'N/A',
            'telefone': proposta.cliente.telefone if proposta.cliente else None,
            'email': proposta.cliente.email if proposta.cliente else None,
            'endereco': proposta.cliente.endereco if proposta.cliente else None,
        },
        'usuario': {
            'nome': proposta.usuario.nome if proposta.usuario else 'N/A',
            'email': proposta.usuario.email if proposta.usuario else 'N/A',
        },
        'itens': [
            {
                'produto_nome': item.produto_nome,
                'descricao': item.descricao,
                'valor': item.valor,
                'rendimento_litros': item.rendimento_litros,
                'custo_por_litro': item.custo_por_litro,
            }
            for item in proposta.itens
        ]
    }
    
    # Gera o PDF
    pdf = PropostaPDF(proposta_data)
    pdf.add_page()
    pdf.titulo_proposta()
    pdf.secao_cliente()
    pdf.secao_vendedor()
    pdf.tabela_produtos()
    pdf.secao_observacoes()
    
    # Retorna o PDF como streaming response
    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin-1'))
    pdf_output.seek(0)
    
    return StreamingResponse(
        pdf_output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=proposta_{proposta_id}.pdf",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.put("/{proposta_id}/", response_model=schemas_proposta.Proposta, summary="Atualiza uma proposta")
def atualizar_proposta(
    proposta_id: int,
    proposta_update: schemas_proposta.PropostaUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma proposta existente"""
    proposta = crud_proposta.update_proposta(db, proposta_id, proposta_update, current_user.id)
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return proposta

@router.delete("/{proposta_id}/", summary="Deleta uma proposta")
def deletar_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta uma proposta"""
    success = crud_proposta.delete_proposta(db, proposta_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return {"message": "Proposta deletada com sucesso"}
