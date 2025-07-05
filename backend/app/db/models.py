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