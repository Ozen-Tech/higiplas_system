# backend/app/db/models.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
from datetime import datetime

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    cnpj = Column(String, unique=True, index=True, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    usuarios = relationship("Usuario", back_populates="empresa")
    produtos = relationship("Produto", back_populates="empresa")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    perfil = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    xp = Column(Integer, default=0) # Pontos de experiência
    level = Column(Integer, default=1) # Nível
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    empresa = relationship("Empresa", back_populates="usuarios")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="usuario")

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    codigo = Column(String, unique=True, index=True)
    categoria = Column(String, index=True)
    descricao = Column(String, nullable=True)
    preco_custo = Column(Float, nullable=True)
    preco_venda = Column(Float)
    unidade_medida = Column(String)
    estoque_minimo = Column(Integer, default=0)
    data_validade = Column(Date, nullable=True)
    quantidade_em_estoque = Column(Integer, default=0)
    
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    empresa = relationship("Empresa", back_populates="produtos")
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    fornecedor = relationship("Fornecedor", back_populates="produtos")
    
    # --- AQUI ESTÁ A ALTERAÇÃO PRINCIPAL ---
    # Adicionamos a opção cascade="all, delete-orphan".
    # Isso diz ao SQLAlchemy: "Quando um Produto for deletado,
    # delete também todas as MovimentacaoEstoque associadas a ele."
    movimentacoes = relationship(
        "MovimentacaoEstoque", 
        back_populates="produto", 
        cascade="all, delete-orphan"
    )
# --- NOVA CLASSE PARA MOVIMENTAÇÕES ---
class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"
    id = Column(Integer, primary_key=True, index=True)
    # Usando Enum para garantir que o tipo seja 'ENTRADA' ou 'SAIDA' no banco
    tipo_movimentacao = Column(Enum('ENTRADA', 'SAIDA', name='tipo_movimentacao_enum'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    observacao = Column(String, nullable=True)
    data_movimentacao = Column(DateTime(timezone=True), server_default=func.now())
    
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    produto = relationship("Produto", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")


class VendaHistorica(Base):
    __tablename__ = "vendas_historicas"

    id = Column(Integer, primary_key=True, index=True)
    ident_antigo = Column(Integer, unique=True, index=True) # Mantém o ID do sistema antigo
    descricao = Column(String, index=True)
    quantidade_vendida_total = Column(Float, default=0)
    custo_compra_total = Column(Float, default=0)
    valor_vendido_total = Column(Float, default=0)
    lucro_bruto_total = Column(Float, default=0)
    margem_lucro_percentual = Column(Float, default=0)

    # Relacionamento opcional com a tabela de produtos atual
    produto_atual_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    produto = relationship("Produto")

class Orcamento(Base):
    __tablename__ = "orcamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String, nullable=False)
    status = Column(String, default="RASCUNHO")  # Ex: RASCUNHO, ENVIADO, APROVADO, REJEITADO
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_validade = Column(Date, nullable=True)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario")
    
    # Relação com os itens do orçamento
    itens = relationship("OrcamentoItem", back_populates="orcamento", cascade="all, delete-orphan")

class OrcamentoItem(Base):
    __tablename__ = "orcamento_itens"

    id = Column(Integer, primary_key=True, index=True)
    quantidade = Column(Integer, nullable=False)
    preco_unitario_congelado = Column(Float, nullable=False) # "Congela" o preço do produto no momento do orçamento

    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"))
    orcamento = relationship("Orcamento", back_populates="itens")
    
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    produto = relationship("Produto")

class Fornecedor(Base):
    __tablename__ = "fornecedores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    cnpj = Column(String, unique=True, nullable=True)
    contato_email = Column(String, nullable=True)
    contato_telefone = Column(String, nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))

    # Relacionamento para saber quais produtos este fornecedor vende
    produtos = relationship("Produto", back_populates="fornecedor")

class OrdemDeCompra(Base):
    __tablename__ = "ordens_compra"
    id = Column(Integer, primary_key=True, index=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    status = Column(String, default="RASCUNHO") # RASCUNHO, ENVIADA, RECEBIDA
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_recebimento = Column(DateTime(timezone=True), nullable=True)
    
    fornecedor = relationship("Fornecedor")
    usuario = relationship("Usuario")
    itens = relationship("OrdemDeCompraItem", back_populates="ordem", cascade="all, delete-orphan")

class OrdemDeCompraItem(Base):
    __tablename__ = "ordens_compra_itens"
    id = Column(Integer, primary_key=True, index=True)
    ordem_id = Column(Integer, ForeignKey("ordens_compra.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade_solicitada = Column(Integer, nullable=False)
    custo_unitario_registrado = Column(Float, nullable=False)

    ordem = relationship("OrdemDeCompra", back_populates="itens")
    produto = relationship("Produto")
