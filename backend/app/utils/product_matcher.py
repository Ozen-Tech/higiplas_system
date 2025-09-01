from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from app.db import models
from typing import Tuple, Optional


def similarity(a: str, b: str) -> float:
    """Calcula a similaridade entre duas strings usando SequenceMatcher."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_product_by_name(db: Session, product_name: str, empresa_id: int, threshold: float = 0.6) -> Tuple[Optional[models.Produto], float]:
    """
    Encontra um produto no banco de dados baseado na similaridade do nome.
    
    Args:
        db: Sessão do banco de dados
        product_name: Nome do produto a ser buscado
        empresa_id: ID da empresa
        threshold: Limite mínimo de similaridade (0.0 a 1.0)
    
    Returns:
        Tuple contendo o produto encontrado (ou None) e o score de similaridade
    """
    if not product_name or product_name.strip() == '':
        return None, 0.0
    
    # Buscar todos os produtos da empresa
    produtos = db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id
    ).all()
    
    best_match = None
    best_score = 0.0
    
    # Calcular similaridade com cada produto
    for produto in produtos:
        if not produto.nome:
            continue
            
        score = similarity(product_name, produto.nome)
        
        if score > best_score and score >= threshold:
            best_match = produto
            best_score = score
    
    return best_match, best_score


def find_product_by_code_or_name(db: Session, codigo: str, descricao: str, empresa_id: int, threshold: float = 0.6) -> Tuple[Optional[models.Produto], str, float]:
    """
    Busca um produto primeiro pelo código, depois pelo nome se não encontrar.
    
    Args:
        db: Sessão do banco de dados
        codigo: Código do produto
        descricao: Descrição/nome do produto
        empresa_id: ID da empresa
        threshold: Limite mínimo de similaridade para busca por nome
    
    Returns:
        Tuple contendo:
        - produto encontrado (ou None)
        - método usado ('codigo', 'nome' ou 'nao_encontrado')
        - score de similaridade (1.0 para código, valor calculado para nome)
    """
    # Primeiro, tentar buscar pelo código
    if codigo:
        produto = db.query(models.Produto).filter(
            models.Produto.codigo == str(codigo),
            models.Produto.empresa_id == empresa_id
        ).first()
        
        if produto:
            return produto, 'codigo', 1.0
    
    # Se não encontrou pelo código, tentar por nome
    if descricao:
        produto, score = find_product_by_name(db, descricao, empresa_id, threshold)
        if produto:
            return produto, 'nome', score
    
    return None, 'nao_encontrado', 0.0