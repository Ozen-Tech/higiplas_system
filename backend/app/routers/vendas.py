# /backend/app/routers/vendas.py
"""
Router para o módulo de vendas mobile
Focado em operações rápidas para vendedores de rua
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..schemas import vendas as schemas
from ..crud import movimentacao_estoque as crud_movimentacao

router = APIRouter(
    prefix="/vendas",
    tags=["Vendas Mobile"]
)

# ============= DASHBOARD DO VENDEDOR =============

@router.get("/dashboard", response_model=schemas.VendedorDashboard)
def get_vendedor_dashboard(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Dashboard do vendedor com estatísticas do dia
    """
    hoje = date.today()
    
    # Buscar vendas do dia (movimentações de saída do vendedor)
    vendas_hoje = db.query(models.MovimentacaoEstoque).join(
        models.Produto
    ).filter(
        models.MovimentacaoEstoque.usuario_id == current_user.id,
        models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
        func.date(models.MovimentacaoEstoque.data_movimentacao) == hoje
    ).all()
    
    # Calcular estatísticas
    total_vendido = 0
    quantidade_pedidos = len(set([v.observacao for v in vendas_hoje if v.observacao]))
    
    for venda in vendas_hoje:
        produto = db.query(models.Produto).filter(
            models.Produto.id == venda.produto_id
        ).first()
        if produto:
            total_vendido += venda.quantidade * produto.preco_venda
    
    # Buscar clientes visitados hoje
    clientes_hoje = db.query(models.Cliente).filter(
        models.Cliente.vendedor_id == current_user.id,
        func.date(models.Cliente.atualizado_em) == hoje
    ).count() if hasattr(models.Cliente, 'atualizado_em') else 0
    
    # Meta do dia (pode vir de configuração)
    meta_dia = 2000.00  # Exemplo fixo, pode ser configurável
    
    return schemas.VendedorDashboard(
        total_vendido_hoje=total_vendido,
        quantidade_pedidos_hoje=quantidade_pedidos,
        clientes_visitados_hoje=clientes_hoje,
        meta_dia=meta_dia,
        progresso_meta=(total_vendido / meta_dia * 100) if meta_dia > 0 else 0
    )

# ============= BUSCA RÁPIDA DE CLIENTES =============

@router.get("/clientes/busca-rapida", response_model=List[schemas.ClienteRapido])
def busca_rapida_clientes(
    termo: Optional[str] = None,
    bairro: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Busca rápida de clientes para o vendedor
    Otimizado para resultados instantâneos
    """
    query = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == current_user.empresa_id,
        models.Cliente.vendedor_id == current_user.id
    )
    
    if termo:
        termo_busca = f"%{termo}%"
        query = query.filter(
            (models.Cliente.razao_social.ilike(termo_busca)) |
            (models.Cliente.telefone.like(termo_busca))
        )
    
    if bairro:
        query = query.filter(models.Cliente.endereco.ilike(f"%{bairro}%"))
    
    clientes = query.order_by(
        models.Cliente.razao_social
    ).limit(limit).all()
    
    # Mapear para resposta simplificada
    resultado = []
    for cliente in clientes:
        # Extrair bairro e cidade do endereço
        bairro_cliente = None
        cidade_cliente = None
        if cliente.endereco:
            partes = cliente.endereco.split(',')
            bairro_cliente = partes[0].strip() if len(partes) > 0 else None
            cidade_cliente = partes[1].strip() if len(partes) > 1 else None
        
        # Buscar última compra
        ultima_venda = db.query(models.MovimentacaoEstoque).join(
            models.Produto
        ).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.observacao.ilike(f"%{cliente.razao_social}%")
        ).order_by(
            desc(models.MovimentacaoEstoque.data_movimentacao)
        ).first()
        
        resultado.append(schemas.ClienteRapido(
            id=cliente.id,
            nome=cliente.razao_social,
            telefone=cliente.telefone or "",
            bairro=bairro_cliente,
            cidade=cidade_cliente,
            ultima_compra=ultima_venda.data_movimentacao if ultima_venda else None
        ))
    
    return resultado

# ============= PRODUTOS DISPONÍVEIS =============

@router.get("/produtos/disponiveis", response_model=List[schemas.ProdutoVenda])
def listar_produtos_venda(
    busca: Optional[str] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Lista produtos disponíveis para venda
    Apenas produtos com estoque > 0
    """
    query = db.query(models.Produto).filter(
        models.Produto.empresa_id == current_user.empresa_id,
        models.Produto.quantidade_em_estoque > 0
    )
    
    if busca:
        termo_busca = f"%{busca}%"
        query = query.filter(
            (models.Produto.nome.ilike(termo_busca)) |
            (models.Produto.codigo.ilike(termo_busca))
        )
    
    if categoria:
        query = query.filter(models.Produto.categoria == categoria)
    
    produtos = query.order_by(models.Produto.nome).all()
    
    return [
        schemas.ProdutoVenda(
            id=p.id,
            nome=p.nome,
            codigo=p.codigo,
            preco=p.preco_venda,
            estoque_disponivel=p.quantidade_em_estoque,
            categoria=p.categoria,
            unidade_medida=p.unidade_medida
        ) for p in produtos
    ]

# ============= REGISTRAR VENDA =============

@router.post("/registrar", response_model=schemas.VendaResponse)
def registrar_venda(
    venda: schemas.VendaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Registra uma venda completa
    - Cria movimentações de saída para cada produto
    - Atualiza estoque
    - Registra histórico do cliente
    """
    try:
        # Validar cliente
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == venda.cliente_id,
            models.Cliente.empresa_id == current_user.empresa_id
        ).first()
        
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Validar estoque de todos os produtos antes de processar
        produtos_info = []
        total_venda = 0
        
        for item in venda.itens:
            produto = db.query(models.Produto).filter(
                models.Produto.id == item.produto_id,
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto ID {item.produto_id} não encontrado"
                )
            
            if produto.quantidade_em_estoque < item.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para {produto.nome}. Disponível: {produto.quantidade_em_estoque}"
                )
            
            produtos_info.append({
                'produto': produto,
                'quantidade': item.quantidade
            })
            total_venda += produto.preco_venda * item.quantidade
        
        # Processar movimentações
        movimentacoes_criadas = []
        observacao_base = f"Venda para {cliente.razao_social}"
        if venda.observacao:
            observacao_base += f" - {venda.observacao}"
        
        for info in produtos_info:
            produto = info['produto']
            quantidade = info['quantidade']
            
            # Criar movimentação de saída
            movimentacao = models.MovimentacaoEstoque(
                produto_id=produto.id,
                tipo_movimentacao='SAIDA',
                quantidade=quantidade,
                observacao=observacao_base,
                usuario_id=current_user.id
            )
            
            # Atualizar estoque
            produto.quantidade_em_estoque -= quantidade
            
            db.add(movimentacao)
            movimentacoes_criadas.append({
                'produto_nome': produto.nome,
                'quantidade': quantidade,
                'valor_unitario': produto.preco_venda,
                'valor_total': produto.preco_venda * quantidade
            })
        
        # Atualizar data de última compra do cliente
        cliente.atualizado_em = datetime.now()
        
        db.commit()
        
        return schemas.VendaResponse(
            sucesso=True,
            mensagem=f"Venda registrada com sucesso! Total: R$ {total_venda:.2f}",
            venda_id=movimentacoes_criadas[0]['produto_nome'] if movimentacoes_criadas else "N/A",
            cliente_nome=cliente.razao_social,
            total_venda=total_venda,
            itens_processados=len(movimentacoes_criadas),
            detalhes=movimentacoes_criadas
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar venda: {str(e)}"
        )

# ============= HISTÓRICO DE VENDAS =============

@router.get("/historico", response_model=List[schemas.VendaHistorico])
def listar_historico_vendas(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    cliente_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Lista histórico de vendas do vendedor
    """
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    
    if not data_fim:
        data_fim = date.today()
    
    # Buscar movimentações de saída
    query = db.query(models.MovimentacaoEstoque).join(
        models.Produto
    ).filter(
        models.MovimentacaoEstoque.usuario_id == current_user.id,
        models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
        func.date(models.MovimentacaoEstoque.data_movimentacao) >= data_inicio,
        func.date(models.MovimentacaoEstoque.data_movimentacao) <= data_fim,
        models.Produto.empresa_id == current_user.empresa_id
    )
    
    movimentacoes = query.order_by(
        desc(models.MovimentacaoEstoque.data_movimentacao)
    ).limit(limit).all()
    
    # Agrupar por venda (usando observação como chave)
    vendas_agrupadas = {}
    
    for mov in movimentacoes:
        chave = f"{mov.data_movimentacao.date()}_{mov.observacao}"
        
        if chave not in vendas_agrupadas:
            vendas_agrupadas[chave] = {
                'data': mov.data_movimentacao,
                'cliente_nome': mov.observacao.replace('Venda para ', '').split(' - ')[0],
                'observacao': mov.observacao,
                'itens': [],
                'total': 0
            }
        
        produto = db.query(models.Produto).filter(
            models.Produto.id == mov.produto_id
        ).first()
        
        if produto:
            valor_item = produto.preco_venda * mov.quantidade
            vendas_agrupadas[chave]['itens'].append({
                'produto': produto.nome,
                'quantidade': mov.quantidade,
                'valor': valor_item
            })
            vendas_agrupadas[chave]['total'] += valor_item
    
    # Converter para lista
    resultado = [
        schemas.VendaHistorico(
            data=v['data'],
            cliente_nome=v['cliente_nome'],
            total=v['total'],
            quantidade_itens=len(v['itens']),
            observacao=v['observacao']
        ) for v in vendas_agrupadas.values()
    ]
    
    return sorted(resultado, key=lambda x: x.data, reverse=True)

# ============= ESTATÍSTICAS =============

@router.get("/estatisticas/periodo", response_model=schemas.EstatisticasVendas)
def estatisticas_periodo(
    dias: int = 30,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Estatísticas de vendas do período
    """
    data_inicio = date.today() - timedelta(days=dias)
    
    # Buscar vendas do período
    vendas = db.query(models.MovimentacaoEstoque).join(
        models.Produto
    ).filter(
        models.MovimentacaoEstoque.usuario_id == current_user.id,
        models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
        func.date(models.MovimentacaoEstoque.data_movimentacao) >= data_inicio,
        models.Produto.empresa_id == current_user.empresa_id
    ).all()
    
    # Calcular estatísticas
    total_vendido = 0
    produtos_vendidos = {}
    
    for venda in vendas:
        produto = db.query(models.Produto).filter(
            models.Produto.id == venda.produto_id
        ).first()
        
        if produto:
            valor = produto.preco_venda * venda.quantidade
            total_vendido += valor
            
            if produto.nome not in produtos_vendidos:
                produtos_vendidos[produto.nome] = {
                    'quantidade': 0,
                    'valor': 0
                }
            
            produtos_vendidos[produto.nome]['quantidade'] += venda.quantidade
            produtos_vendidos[produto.nome]['valor'] += valor
    
    # Top 5 produtos
    top_produtos = sorted(
        [
            {'produto': k, 'quantidade': v['quantidade'], 'valor_total': v['valor']}
            for k, v in produtos_vendidos.items()
        ],
        key=lambda x: x['valor_total'],
        reverse=True
    )[:5]
    
    quantidade_vendas = len(set([v.observacao for v in vendas]))
    ticket_medio = total_vendido / quantidade_vendas if quantidade_vendas > 0 else 0
    
    return schemas.EstatisticasVendas(
        total_vendido=total_vendido,
        quantidade_vendas=quantidade_vendas,
        ticket_medio=ticket_medio,
        produtos_mais_vendidos=top_produtos
    )
