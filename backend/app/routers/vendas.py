# backend/app/routers/vendas.py
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
    hoje = date.today()
    
    vendas_hoje = db.query(models.MovimentacaoEstoque).join(
        models.Produto
    ).filter(
        models.MovimentacaoEstoque.usuario_id == current_user.id,
        models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
        func.date(models.MovimentacaoEstoque.data_movimentacao) == hoje
    ).all()
    
    total_vendido = 0
    quantidade_pedidos = len(set([v.observacao for v in vendas_hoje if v.observacao]))
    
    for venda in vendas_hoje:
        produto = db.query(models.Produto).filter(models.Produto.id == venda.produto_id).first()
        if produto:
            total_vendido += venda.quantidade * produto.preco_venda
    
    clientes_hoje = db.query(models.Cliente).filter(
        models.Cliente.vendedor_id == current_user.id,
        func.date(models.Cliente.atualizado_em) == hoje
    ).count() if hasattr(models.Cliente, 'atualizado_em') else 0
    
    meta_dia = 2000.00  # Ajustável
    
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
    
    clientes = query.order_by(models.Cliente.razao_social).limit(limit).all()
    
    resultado = []
    for cliente in clientes:
        bairro_cliente = None
        cidade_cliente = None
        if cliente.endereco:
            partes = cliente.endereco.split(',')
            bairro_cliente = partes[0].strip() if len(partes) > 0 else None
            cidade_cliente = partes[1].strip() if len(partes) > 1 else None
        
        ultima_venda = db.query(models.MovimentacaoEstoque).join(models.Produto).filter(
            models.MovimentacaoEstoque.tipo_movimentacao == 'SAIDA',
            models.MovimentacaoEstoque.observacao.ilike(f"%{cliente.razao_social}%")
        ).order_by(desc(models.MovimentacaoEstoque.data_movimentacao)).first()
        
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

def calcular_estatisticas_preco(produto_id: int, empresa_id: int, db: Session) -> dict:
    """Calcula estatísticas de preços de um produto baseado no histórico de vendas"""
    try:
        # Verificar se a tabela existe (pode não existir ainda se a migration não foi executada)
        historico = db.query(models.HistoricoPrecoProduto).filter(
            models.HistoricoPrecoProduto.produto_id == produto_id,
            models.HistoricoPrecoProduto.empresa_id == empresa_id
        ).all()
        
        if not historico:
            return {
                'preco_maior': None,
                'preco_medio': None,
                'preco_menor': None,
                'total_vendas': 0
            }
        
        precos = [h.preco_unitario for h in historico]
        
        return {
            'preco_maior': max(precos),
            'preco_medio': sum(precos) / len(precos),
            'preco_menor': min(precos),
            'total_vendas': len(historico)
        }
    except Exception as e:
        # Se a tabela não existir ou houver qualquer erro, retornar valores vazios
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Erro ao calcular estatísticas de preço (tabela pode não existir): {str(e)}")
        return {
            'preco_maior': None,
            'preco_medio': None,
            'preco_menor': None,
            'total_vendas': 0
        }

@router.get("/produtos/disponiveis", response_model=List[schemas.ProdutoVenda])
def listar_produtos_venda(
    busca: Optional[str] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    query = db.query(models.Produto).filter(
        models.Produto.empresa_id == current_user.empresa_id,
        # CORREÇÃO: Remover filtro de estoque > 0 para permitir orçamentos com produtos zerados
        # models.Produto.quantidade_em_estoque > 0  # <-- COMENTAR OU REMOVER ESTA LINHA
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
    
    resultado = []
    for p in produtos:
        try:
            # Calcular estatísticas de preço
            estatisticas_dict = calcular_estatisticas_preco(p.id, current_user.empresa_id, db)
            # Sempre criar o objeto de estatísticas, mesmo que os valores sejam None
            estatisticas = schemas.EstatisticasPreco(**estatisticas_dict)
            
            produto_venda = schemas.ProdutoVenda(
                id=p.id,
                nome=p.nome,
                codigo=p.codigo,
                preco=p.preco_venda,
                estoque_disponivel=p.quantidade_em_estoque,
                categoria=p.categoria,
                unidade_medida=p.unidade_medida,
                estatisticas_preco=estatisticas
            )
            
            resultado.append(produto_venda)
        except Exception as e:
            # Se houver erro ao calcular estatísticas, retornar produto com estatísticas vazias
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao calcular estatísticas para produto {p.id}: {str(e)}")
            
            # Criar estatísticas vazias em caso de erro
            estatisticas_vazias = schemas.EstatisticasPreco(
                preco_maior=None,
                preco_medio=None,
                preco_menor=None,
                total_vendas=0
            )
            
            produto_venda = schemas.ProdutoVenda(
                id=p.id,
                nome=p.nome,
                codigo=p.codigo,
                preco=p.preco_venda,
                estoque_disponivel=p.quantidade_em_estoque,
                categoria=p.categoria,
                unidade_medida=p.unidade_medida,
                estatisticas_preco=estatisticas_vazias
            )
            
            resultado.append(produto_venda)
    
    return resultado
    
# ============= REGISTRAR VENDA =============

@router.post("/registrar", response_model=schemas.VendaResponse)
def registrar_venda(
    venda: schemas.VendaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    try:
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == venda.cliente_id,
            models.Cliente.empresa_id == current_user.empresa_id
        ).first()
        
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
        
        produtos_info = []
        total_venda = 0
        
        for item in venda.itens:
            produto = db.query(models.Produto).filter(
                models.Produto.id == item.produto_id,
                models.Produto.empresa_id == current_user.empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produto ID {item.produto_id} não encontrado")
            
            if produto.quantidade_em_estoque < item.quantidade:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estoque insuficiente para {produto.nome}")
            
            produtos_info.append({'produto': produto, 'quantidade': item.quantidade})
            total_venda += produto.preco_venda * item.quantidade
        
        movimentacoes_criadas = []
        observacao_base = f"Venda para {cliente.razao_social}"
        if venda.observacao:
            observacao_base += f" - {venda.observacao}"
        
        for info in produtos_info:
            produto = info['produto']
            quantidade = info['quantidade']
            quantidade_antes = produto.quantidade_em_estoque
            quantidade_depois = produto.quantidade_em_estoque - quantidade

            movimentacao = models.MovimentacaoEstoque(
                produto_id=produto.id,
                tipo_movimentacao='SAIDA',
                quantidade=quantidade,
                quantidade_antes=quantidade_antes,
                quantidade_depois=quantidade_depois,
                origem='VENDA',
                observacao=observacao_base,
                usuario_id=current_user.id
            )
            produto.quantidade_em_estoque = quantidade_depois
            db.add(movimentacao)
            movimentacoes_criadas.append({
                'produto_nome': produto.nome,
                'quantidade': quantidade,
                'valor_unitario': produto.preco_venda,
                'valor_total': produto.preco_venda * quantidade
            })
        
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
        raise HTTPException(status_code=500, detail=str(e))
