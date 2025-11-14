# backend/app/crud/ficha_tecnica.py

from sqlalchemy.orm import Session
from typing import Optional, List
from ..schemas import proposta_detalhada as schemas
from ..db import models
from ..services.ficha_tecnica_service import ficha_tecnica_service
from ..core.logger import app_logger

logger = app_logger


def create_ficha_tecnica(db: Session, ficha_in: schemas.FichaTecnicaCreate) -> models.FichaTecnica:
    """Cria uma nova ficha técnica"""
    db_ficha = models.FichaTecnica(**ficha_in.model_dump())
    db.add(db_ficha)
    db.commit()
    db.refresh(db_ficha)
    return db_ficha


def get_ficha_by_id(db: Session, ficha_id: int) -> Optional[models.FichaTecnica]:
    """Busca uma ficha técnica por ID"""
    return db.query(models.FichaTecnica).filter(models.FichaTecnica.id == ficha_id).first()


def get_ficha_by_produto(db: Session, produto_id: int) -> Optional[models.FichaTecnica]:
    """Busca ficha técnica de um produto"""
    return db.query(models.FichaTecnica).filter(
        models.FichaTecnica.produto_id == produto_id
    ).first()


def get_ficha_by_nome(db: Session, nome_produto: str) -> Optional[models.FichaTecnica]:
    """Busca ficha técnica pelo nome do produto"""
    return db.query(models.FichaTecnica).filter(
        models.FichaTecnica.nome_produto.ilike(f"%{nome_produto}%")
    ).first()


def get_all_fichas(db: Session, skip: int = 0, limit: int = 100) -> List[models.FichaTecnica]:
    """Lista todas as fichas técnicas"""
    return db.query(models.FichaTecnica).offset(skip).limit(limit).all()


def update_ficha_tecnica(
    db: Session, 
    ficha_id: int, 
    ficha_update: schemas.FichaTecnicaUpdate
) -> Optional[models.FichaTecnica]:
    """Atualiza uma ficha técnica"""
    db_ficha = db.query(models.FichaTecnica).filter(
        models.FichaTecnica.id == ficha_id
    ).first()
    
    if not db_ficha:
        return None
    
    update_data = ficha_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ficha, key, value)
    
    db.commit()
    db.refresh(db_ficha)
    return db_ficha


def delete_ficha_tecnica(db: Session, ficha_id: int) -> bool:
    """Deleta uma ficha técnica"""
    db_ficha = db.query(models.FichaTecnica).filter(
        models.FichaTecnica.id == ficha_id
    ).first()
    
    if not db_ficha:
        return False
    
    db.delete(db_ficha)
    db.commit()
    return True


def processar_pdf_ficha_tecnica(db: Session, pdf_path: str, produto_id: Optional[int] = None) -> models.FichaTecnica:
    """
    Processa um PDF de ficha técnica e cria/atualiza registro no banco
    """
    try:
        # Extrair dados do PDF
        dados = ficha_tecnica_service.extrair_dados_pdf(pdf_path)
        
        # Verificar se já existe ficha com mesmo nome ou produto
        ficha_existente = None
        if produto_id:
            ficha_existente = get_ficha_by_produto(db, produto_id)
        if not ficha_existente:
            ficha_existente = get_ficha_by_nome(db, dados['nome_produto'])
        
        # Se existe, atualizar; senão, criar nova
        if ficha_existente:
            # Atualizar dados
            for key, value in dados.items():
                if key != 'nome_produto' or not ficha_existente.nome_produto:
                    setattr(ficha_existente, key, value)
            if produto_id:
                ficha_existente.produto_id = produto_id
            db.commit()
            db.refresh(ficha_existente)
            logger.info(f"Ficha técnica atualizada: {ficha_existente.nome_produto}")
            return ficha_existente
        else:
            # Criar nova
            dados['produto_id'] = produto_id
            ficha_create = schemas.FichaTecnicaCreate(**dados)
            nova_ficha = create_ficha_tecnica(db, ficha_create)
            logger.info(f"Nova ficha técnica criada: {nova_ficha.nome_produto}")
            return nova_ficha
            
    except Exception as e:
        logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
        raise

