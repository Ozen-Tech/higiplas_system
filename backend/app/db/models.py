# backend/app/db/models.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Date, Enum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
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
    movimentacoes = relationship(
        "MovimentacaoEstoque", 
        back_populates="usuario", 
        primaryjoin="Usuario.id == MovimentacaoEstoque.usuario_id"
    )

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
    
    # Campos de aprovação
    status = Column(Enum('PENDENTE', 'CONFIRMADO', 'REJEITADO', name='status_movimentacao_enum'), nullable=False, default='CONFIRMADO')
    aprovado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    data_aprovacao = Column(DateTime(timezone=True), nullable=True)
    motivo_rejeicao = Column(String, nullable=True)
    motivo_movimentacao = Column(Enum('CARREGAMENTO', 'DEVOLUCAO', 'AJUSTE_FISICO', 'PERDA_AVARIA', 'TRANSFERENCIA_INTERNA', name='motivo_movimentacao_enum'), nullable=True)
    observacao_motivo = Column(String, nullable=True)
    dados_antes_edicao = Column(JSON, nullable=True)
    dados_depois_edicao = Column(JSON, nullable=True)
    
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    produto = relationship("Produto", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes", foreign_keys=[usuario_id])
    aprovado_por = relationship("Usuario", foreign_keys=[aprovado_por_id])


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
    # Removido cascade para evitar problemas com colunas faltantes no banco
    historico_pagamentos = relationship("HistoricoPagamento", back_populates="cliente")

class HistoricoPagamento(Base):
    __tablename__ = "historico_pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    data_vencimento = Column(Date, nullable=True)  # Tornado nullable para compatibilidade
    data_pagamento = Column(Date, nullable=True)
    status = Column(Enum('PENDENTE', 'PAGO', 'ATRASADO', name='status_pagamento_historico_enum'), default='PENDENTE')
    numero_nf = Column(String, nullable=True)
    observacoes = Column(String, nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    cliente = relationship("Cliente", back_populates="historico_pagamentos")
    
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"), nullable=True)
    orcamento = relationship("Orcamento")

class PrecoClienteProduto(Base):
    """Armazena preços padrão e ranges calculados por cliente-produto"""
    __tablename__ = "precos_cliente_produto"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    preco_padrao = Column(Float, nullable=False)  # Preço padrão (último preço confirmado)
    preco_minimo = Column(Float, nullable=True)  # Menor preço já vendido
    preco_maximo = Column(Float, nullable=True)  # Maior preço já vendido
    preco_medio = Column(Float, nullable=True)  # Preço médio calculado
    
    total_vendas = Column(Integer, default=0)  # Total de vendas confirmadas
    data_ultima_venda = Column(DateTime(timezone=True), nullable=True)
    
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    cliente = relationship("Cliente")
    produto = relationship("Produto")
    
    __table_args__ = (
        Index('idx_preco_cliente_produto', 'cliente_id', 'produto_id'),
        Index('idx_preco_produto', 'produto_id'),
        UniqueConstraint('cliente_id', 'produto_id', name='uq_cliente_produto'),
    )

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

class HistoricoVendaCliente(Base):
    """Armazena histórico de vendas por vendedor-cliente-produto para análise e sugestões"""
    __tablename__ = "historico_vendas_cliente"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos principais
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Dados da venda
    quantidade_vendida = Column(Integer, nullable=False)
    preco_unitario_vendido = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)
    data_venda = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    vendedor = relationship("Usuario", foreign_keys=[vendedor_id])
    cliente = relationship("Cliente")
    produto = relationship("Produto")
    orcamento = relationship("Orcamento")
    empresa = relationship("Empresa")
    
    # Índices compostos para otimização de consultas
    __table_args__ = (
        # Índice para consultas por vendedor-cliente-produto (sugestões)
        Index('idx_vendedor_cliente_produto', 'vendedor_id', 'cliente_id', 'produto_id'),
        # Índice para consultas por cliente-produto (análise de cliente)
        Index('idx_cliente_produto', 'cliente_id', 'produto_id'),
        # Índice para consultas de frequência (cliente + data)
        Index('idx_cliente_data', 'cliente_id', 'data_venda'),
        # Índice para análise de demanda (produto + data)
        Index('idx_produto_data', 'produto_id', 'data_venda'),
    )

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
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
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

class FichaTecnica(Base):
    """Armazena informações técnicas dos produtos Girassol extraídas das fichas técnicas"""
    __tablename__ = "fichas_tecnicas"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True, index=True)
    nome_produto = Column(String, nullable=False, index=True)  # Nome do produto conforme PDF
    dilucao_recomendada = Column(String, nullable=True)  # Ex: "1:10", "1 litro para 10 litros"
    dilucao_numerador = Column(Float, nullable=True)  # Parte 1 da diluição (ex: 1)
    dilucao_denominador = Column(Float, nullable=True)  # Parte 2 da diluição (ex: 10)
    rendimento_litro = Column(Float, nullable=True)  # Quantos litros rende por litro do produto
    modo_uso = Column(String, nullable=True)  # Descrição do modo de uso
    arquivo_pdf_path = Column(String, nullable=True)  # Caminho do arquivo PDF original
    observacoes = Column(String, nullable=True)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamento
    produto = relationship("Produto")
    
    # Índices
    __table_args__ = (
        Index('idx_ficha_produto', 'produto_id'),
        Index('idx_ficha_nome', 'nome_produto'),
    )

class ProdutoConcorrente(Base):
    """Armazena informações sobre produtos concorrentes para comparação"""
    __tablename__ = "produtos_concorrentes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    marca = Column(String, nullable=True)
    preco_medio = Column(Float, nullable=True)  # Preço médio no mercado
    rendimento_litro = Column(Float, nullable=True)  # Rendimento por litro
    dilucao = Column(String, nullable=True)  # Diluição recomendada
    dilucao_numerador = Column(Float, nullable=True)
    dilucao_denominador = Column(Float, nullable=True)
    categoria = Column(String, nullable=True, index=True)  # Para agrupar produtos similares
    observacoes = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)  # Para desativar sem deletar
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Índices
    __table_args__ = (
        Index('idx_concorrente_categoria', 'categoria'),
        Index('idx_concorrente_ativo', 'ativo'),
    )

class PropostaDetalhada(Base):
    """Armazena propostas detalhadas criadas pelos vendedores"""
    __tablename__ = "propostas_detalhadas"
    
    id = Column(Integer, primary_key=True, index=True)
    orcamento_id = Column(Integer, ForeignKey("orcamentos.id"), nullable=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    ficha_tecnica_id = Column(Integer, ForeignKey("fichas_tecnicas.id"), nullable=True)
    
    # Dados da proposta
    quantidade_produto = Column(Float, nullable=False)  # Quantidade do produto (em litros/unidades)
    dilucao_aplicada = Column(String, nullable=True)  # Diluição aplicada na proposta
    dilucao_numerador = Column(Float, nullable=True)
    dilucao_denominador = Column(Float, nullable=True)
    rendimento_total_litros = Column(Float, nullable=True)  # Rendimento total calculado
    preco_produto = Column(Float, nullable=True)  # Preço do produto no momento da proposta
    custo_por_litro_final = Column(Float, nullable=True)  # Custo por litro após diluição
    
    # Comparação com concorrentes
    concorrente_id = Column(Integer, ForeignKey("produtos_concorrentes.id"), nullable=True)
    economia_vs_concorrente = Column(Float, nullable=True)  # Economia em percentual ou valor
    economia_percentual = Column(Float, nullable=True)  # Economia em percentual
    economia_valor = Column(Float, nullable=True)  # Economia em valor (R$)
    
    # Informações adicionais
    observacoes = Column(String, nullable=True)
    compartilhavel = Column(Boolean, default=False)  # Se pode ser compartilhada com cliente
    token_compartilhamento = Column(String, unique=True, nullable=True, index=True)  # Token para link compartilhável
    
    # Timestamps
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    orcamento = relationship("Orcamento")
    cliente = relationship("Cliente")
    vendedor = relationship("Usuario", foreign_keys=[vendedor_id])
    produto = relationship("Produto")
    ficha_tecnica = relationship("FichaTecnica")
    concorrente = relationship("ProdutoConcorrente")
    itens = relationship(
        "PropostaDetalhadaItem",
        back_populates="proposta",
        cascade="all, delete-orphan",
        order_by="PropostaDetalhadaItem.id",
    )
    concorrentes_personalizados = relationship(
        "PropostaConcorrenteManual",
        back_populates="proposta",
        cascade="all, delete-orphan",
        order_by="PropostaConcorrenteManual.id",
    )
    
    # Índices compostos
    __table_args__ = (
        Index('idx_proposta_vendedor_cliente', 'vendedor_id', 'cliente_id'),
        Index('idx_proposta_produto', 'produto_id'),
        Index('idx_proposta_data', 'data_criacao'),
    )


class PropostaDetalhadaItem(Base):
    """Itens individuais vinculados a uma proposta detalhada"""
    __tablename__ = "propostas_detalhadas_itens"

    id = Column(Integer, primary_key=True, index=True)
    proposta_id = Column(Integer, ForeignKey("propostas_detalhadas.id", ondelete="CASCADE"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    quantidade_produto = Column(Float, nullable=False)
    dilucao_aplicada = Column(String, nullable=True)
    dilucao_numerador = Column(Float, nullable=True)
    dilucao_denominador = Column(Float, nullable=True)
    rendimento_total_litros = Column(Float, nullable=True)
    preco_produto = Column(Float, nullable=True)
    custo_por_litro_final = Column(Float, nullable=True)
    observacoes = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    concorrente_nome_manual = Column(String, nullable=True)
    concorrente_rendimento_manual = Column(Float, nullable=True)
    concorrente_custo_por_litro_manual = Column(Float, nullable=True)

    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    proposta = relationship("PropostaDetalhada", back_populates="itens")
    produto = relationship("Produto")

    __table_args__ = (
        Index('idx_proposta_item_produto', 'proposta_id', 'produto_id'),
    )


class PropostaConcorrenteManual(Base):
    """Informações manuais de concorrentes adicionadas em uma proposta detalhada"""
    __tablename__ = "propostas_detalhadas_concorrentes"

    id = Column(Integer, primary_key=True, index=True)
    proposta_id = Column(Integer, ForeignKey("propostas_detalhadas.id", ondelete="CASCADE"), nullable=False, index=True)
    nome = Column(String, nullable=False)
    rendimento_litro = Column(Float, nullable=True)
    custo_por_litro = Column(Float, nullable=True)
    observacoes = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    proposta = relationship("PropostaDetalhada", back_populates="concorrentes_personalizados")

    __table_args__ = (
        Index('idx_proposta_concorrente_manual', 'proposta_id', 'nome'),
    )
