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
    tipo_movimentacao = Column(Enum('ENTRADA', 'SAIDA', name='tipo_movimentacao_enum'), nullable=False)
    quantidade = Column(Float, nullable=False)
    observacao = Column(String, nullable=True)
    data_movimentacao = Column(DateTime(timezone=True), server_default=func.now())
    origem = Column(Enum('VENDA', 'DEVOLUCAO', 'CORRECAO_MANUAL', 'COMPRA', 'AJUSTE', 'OUTRO', name='origem_movimentacao_enum'), nullable=True)
    quantidade_antes = Column(Float, nullable=True)
    quantidade_depois = Column(Float, nullable=True)
    
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

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    razao_social = Column(String, nullable=False, index=True)
    cnpj = Column(String, unique=True, index=True, nullable=True)
    endereco = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telefone = Column(String, nullable=True, index=True)  # Adicionado index
    empresa_vinculada = Column(Enum('HIGIPLAS', 'HIGITEC', name='empresa_vinculada_enum'), nullable=False)
    status_pagamento = Column(Enum('BOM_PAGADOR', 'MAU_PAGADOR', name='status_pagamento_enum'), default='BOM_PAGADOR')
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    
    # Novos campos v2
    observacoes = Column(String(500), nullable=True)
    referencia_localizacao = Column(String(200), nullable=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    atualizado_em = Column(DateTime(timezone=True), nullable=True)
    
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    empresa = relationship("Empresa")
    vendedor = relationship("Usuario", foreign_keys=[vendedor_id])
    
    # Relacionamentos
    orcamentos = relationship("Orcamento", back_populates="cliente")
    historico_pagamentos = relationship("HistoricoPagamento", back_populates="cliente", cascade="all, delete-orphan")

class HistoricoPagamento(Base):
    __tablename__ = "historico_pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    status = Column(Enum('PENDENTE', 'PAGO', 'ATRASADO', name='status_pagamento_historico_enum'), default='PENDENTE')
    numero_nf = Column(String, nullable=True)
    observacoes = Column(String, nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    cliente = relationship("Cliente", back_populates="historico_pagamentos")
    
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"), nullable=True)
    orcamento = relationship("Orcamento")

class Orcamento(Base):
    __tablename__ = "orcamentos"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="RASCUNHO")  # Ex: RASCUNHO, ENVIADO, APROVADO, REJEITADO, FINALIZADO
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_validade = Column(Date, nullable=True)
    condicao_pagamento = Column(String, nullable=False)  # Ex: "À vista", "30 dias", "60 dias"
    preco_minimo = Column(Float, nullable=True)
    preco_maximo = Column(Float, nullable=True)
    numero_nf = Column(String, nullable=True)  # NF para dar baixa no orçamento
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario")
    
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    cliente = relationship("Cliente", back_populates="orcamentos")
    
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

class ProdutoMaisVendido(Base):
    __tablename__ = "produtos_mais_vendidos"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    produto = relationship("Produto")
    
    ano = Column(Integer, nullable=False)
    quantidade_vendida = Column(Integer, default=0)
    valor_total_vendido = Column(Float, default=0.0)
    numero_vendas = Column(Integer, default=0)
    ultima_atualizacao = Column(DateTime(timezone=True), server_default=func.now())

class HistoricoPrecoProduto(Base):
    """Armazena histórico de preços de produtos baseado em vendas (NFs de saída)"""
    __tablename__ = "historico_preco_produto"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    produto = relationship("Produto")
    
    preco_unitario = Column(Float, nullable=False)  # Preço unitário vendido
    quantidade = Column(Float, nullable=False)  # Quantidade vendida
    valor_total = Column(Float, nullable=False)  # Valor total da venda
    
    nota_fiscal = Column(String, nullable=True, index=True)  # Número da NF
    data_venda = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    empresa = relationship("Empresa")
    
    # Campos opcionais para contexto
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente")
    
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

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
