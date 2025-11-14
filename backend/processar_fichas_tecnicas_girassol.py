#!/usr/bin/env python3
# backend/processar_fichas_tecnicas_girassol.py

"""
Script para processar PDFs de fichas técnicas da pasta anexada e popular o banco de dados.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.crud import ficha_tecnica as crud_ficha
from app.services.ficha_tecnica_service import ficha_tecnica_service
from app.db import models
from app.core.logger import app_logger
from fuzzywuzzy import fuzz, process

logger = app_logger


def encontrar_produto_por_nome(db: Session, nome_produto: str) -> models.Produto:
    """
    Tenta encontrar um produto no banco pelo nome usando fuzzy matching.
    Retorna o produto mais similar ou None.
    """
    produtos = db.query(models.Produto).all()
    
    if not produtos:
        return None
    
    # Criar lista de nomes de produtos
    nomes_produtos = [(p.id, p.nome) for p in produtos]
    
    # Buscar melhor match
    melhor_match = process.extractOne(
        nome_produto,
        [nome for _, nome in nomes_produtos],
        scorer=fuzz.token_sort_ratio
    )
    
    if melhor_match and melhor_match[1] >= 60:  # Threshold de 60% de similaridade
        # Encontrar o produto correspondente
        produto_id = next(
            (pid for pid, nome in nomes_produtos if nome == melhor_match[0]),
            None
        )
        if produto_id:
            return db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    
    return None


def processar_pasta_fichas_tecnicas(pasta_pdfs: str, db: Session):
    """
    Processa todos os PDFs de uma pasta e cria fichas técnicas no banco.
    Tenta fazer matching automático com produtos existentes.
    """
    if not os.path.isdir(pasta_pdfs):
        logger.error(f"Pasta não encontrada: {pasta_pdfs}")
        return
    
    arquivos_pdf = [f for f in os.listdir(pasta_pdfs) if f.lower().endswith('.pdf')]
    
    logger.info(f"Encontrados {len(arquivos_pdf)} arquivos PDF na pasta {pasta_pdfs}")
    
    fichas_processadas = 0
    fichas_criadas = 0
    fichas_atualizadas = 0
    erros = 0
    
    for arquivo in arquivos_pdf:
        caminho_completo = os.path.join(pasta_pdfs, arquivo)
        
        try:
            logger.info(f"Processando: {arquivo}")
            
            # Extrair dados do PDF
            dados = ficha_tecnica_service.extrair_dados_pdf(caminho_completo)
            
            # Tentar encontrar produto correspondente
            produto = encontrar_produto_por_nome(db, dados['nome_produto'])
            produto_id = produto.id if produto else None
            
            if produto:
                logger.info(f"Produto encontrado: {produto.nome} (ID: {produto.id})")
            else:
                logger.warning(f"Produto não encontrado para: {dados['nome_produto']}")
            
            # Verificar se já existe ficha técnica
            ficha_existente = None
            if produto_id:
                ficha_existente = crud_ficha.get_ficha_by_produto(db, produto_id)
            
            if not ficha_existente:
                ficha_existente = crud_ficha.get_ficha_by_nome(db, dados['nome_produto'])
            
            # Criar ou atualizar
            if ficha_existente:
                # Atualizar
                from app.schemas import proposta_detalhada as schemas
                ficha_update = schemas.FichaTecnicaUpdate(**dados)
                ficha_atualizada = crud_ficha.update_ficha_tecnica(db, ficha_existente.id, ficha_update)
                if ficha_atualizada:
                    if produto_id and not ficha_atualizada.produto_id:
                        ficha_atualizada.produto_id = produto_id
                        db.commit()
                    fichas_atualizadas += 1
                    logger.info(f"Ficha técnica atualizada: {ficha_atualizada.nome_produto}")
            else:
                # Criar nova
                from app.schemas import proposta_detalhada as schemas
                dados['produto_id'] = produto_id
                ficha_create = schemas.FichaTecnicaCreate(**dados)
                nova_ficha = crud_ficha.create_ficha_tecnica(db, ficha_create)
                fichas_criadas += 1
                logger.info(f"Nova ficha técnica criada: {nova_ficha.nome_produto}")
            
            fichas_processadas += 1
            
        except Exception as e:
            erros += 1
            logger.error(f"Erro ao processar {arquivo}: {e}")
            continue
    
    logger.info(f"\n=== Resumo do Processamento ===")
    logger.info(f"Total processados: {fichas_processadas}")
    logger.info(f"Fichas criadas: {fichas_criadas}")
    logger.info(f"Fichas atualizadas: {fichas_atualizadas}")
    logger.info(f"Erros: {erros}")


def main():
    """Função principal"""
    # Caminho padrão da pasta de PDFs
    pasta_pdfs = "/Users/ozen/Downloads/FICHAS TECNICAS - GIRASSOL"
    
    # Permitir passar pasta como argumento
    if len(sys.argv) > 1:
        pasta_pdfs = sys.argv[1]
    
    if not os.path.isdir(pasta_pdfs):
        print(f"Erro: Pasta não encontrada: {pasta_pdfs}")
        print(f"Uso: python processar_fichas_tecnicas_girassol.py [caminho_da_pasta]")
        sys.exit(1)
    
    # Obter sessão do banco
    db = next(get_db())
    
    try:
        processar_pasta_fichas_tecnicas(pasta_pdfs, db)
        print("\nProcessamento concluído com sucesso!")
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        print(f"\nErro: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

