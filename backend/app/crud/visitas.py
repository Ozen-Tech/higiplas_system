"""
CRUD para sistema de visitas de vendedores.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.db import models
from app.schemas import visitas as schemas


def create_visita(
    db: Session,
    visita: schemas.VisitaVendedorCreate
) -> models.VisitaVendedor:
    """Cria uma nova visita de vendedor."""
    db_visita = models.VisitaVendedor(
        vendedor_id=visita.vendedor_id,
        cliente_id=visita.cliente_id,
        latitude=visita.latitude,
        longitude=visita.longitude,
        endereco_completo=visita.endereco_completo,
        motivo_visita=visita.motivo_visita,
        observacoes=visita.observacoes,
        foto_comprovante=visita.foto_comprovante,
        confirmada=visita.confirmada,
        empresa_id=visita.empresa_id,
        data_visita=datetime.now()
    )
    
    db.add(db_visita)
    db.commit()
    db.refresh(db_visita)
    
    return db_visita


def get_visita_by_id(
    db: Session,
    visita_id: int,
    empresa_id: int
) -> Optional[models.VisitaVendedor]:
    """Busca visita por ID."""
    return db.query(models.VisitaVendedor).filter(
        models.VisitaVendedor.id == visita_id,
        models.VisitaVendedor.empresa_id == empresa_id
    ).first()


def get_visitas_by_vendedor(
    db: Session,
    vendedor_id: int,
    empresa_id: int,
    confirmada: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> List[models.VisitaVendedor]:
    """Lista visitas de um vendedor."""
    query = db.query(models.VisitaVendedor).filter(
        models.VisitaVendedor.vendedor_id == vendedor_id,
        models.VisitaVendedor.empresa_id == empresa_id
    )
    
    if confirmada is not None:
        query = query.filter(models.VisitaVendedor.confirmada == confirmada)
    
    return query.order_by(
        models.VisitaVendedor.data_visita.desc()
    ).offset(offset).limit(limit).all()


def get_visitas_confirmadas(
    db: Session,
    empresa_id: int,
    vendedor_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 1000
) -> List[models.VisitaVendedor]:
    """Lista visitas confirmadas (para exibir no mapa)."""
    query = db.query(models.VisitaVendedor).filter(
        models.VisitaVendedor.empresa_id == empresa_id,
        models.VisitaVendedor.confirmada == True
    )
    
    if vendedor_id:
        query = query.filter(models.VisitaVendedor.vendedor_id == vendedor_id)
    
    if cliente_id:
        query = query.filter(models.VisitaVendedor.cliente_id == cliente_id)
    
    if data_inicio:
        query = query.filter(models.VisitaVendedor.data_visita >= data_inicio)
    
    if data_fim:
        # Adiciona 1 dia para incluir o dia final completo
        data_fim_completa = datetime.combine(data_fim, datetime.max.time())
        query = query.filter(models.VisitaVendedor.data_visita <= data_fim_completa)
    
    return query.order_by(
        models.VisitaVendedor.data_visita.desc()
    ).limit(limit).all()


def update_visita(
    db: Session,
    visita_id: int,
    empresa_id: int,
    visita_update: schemas.VisitaVendedorUpdate
) -> Optional[models.VisitaVendedor]:
    """Atualiza uma visita (apenas se não confirmada)."""
    visita = get_visita_by_id(db, visita_id, empresa_id)
    
    if not visita:
        return None
    
    # Não permitir edição de visitas confirmadas
    if visita.confirmada:
        raise ValueError("Não é possível editar uma visita confirmada")
    
    # Atualizar campos fornecidos
    if visita_update.cliente_id is not None:
        visita.cliente_id = visita_update.cliente_id
    
    if visita_update.motivo_visita is not None:
        visita.motivo_visita = visita_update.motivo_visita
    
    if visita_update.observacoes is not None:
        visita.observacoes = visita_update.observacoes
    
    if visita_update.foto_comprovante is not None:
        visita.foto_comprovante = visita_update.foto_comprovante
    
    visita.atualizado_em = datetime.now()
    
    db.commit()
    db.refresh(visita)
    
    return visita


def confirmar_visita(
    db: Session,
    visita_id: int,
    empresa_id: int
) -> Optional[models.VisitaVendedor]:
    """Confirma uma visita (marca como confirmada, não permite mais edição)."""
    visita = get_visita_by_id(db, visita_id, empresa_id)
    
    if not visita:
        return None
    
    visita.confirmada = True
    visita.atualizado_em = datetime.now()
    
    db.commit()
    db.refresh(visita)
    
    return visita


def get_visitas_stats(
    db: Session,
    vendedor_id: Optional[int],
    empresa_id: int,
    periodo_dias: int = 30
) -> dict:
    """Calcula estatísticas de visitas."""
    agora = datetime.now()
    hoje = agora.date()
    semana_inicio = hoje - timedelta(days=7)
    mes_inicio = hoje - timedelta(days=periodo_dias)
    
    query = db.query(models.VisitaVendedor).filter(
        models.VisitaVendedor.empresa_id == empresa_id
    )
    
    if vendedor_id:
        query = query.filter(models.VisitaVendedor.vendedor_id == vendedor_id)
    
    # Total de visitas
    total_visitas = query.count()
    
    # Visitas confirmadas e pendentes
    visitas_confirmadas = query.filter(
        models.VisitaVendedor.confirmada == True
    ).count()
    
    visitas_pendentes = total_visitas - visitas_confirmadas
    
    # Visitas hoje
    visitas_hoje = query.filter(
        func.date(models.VisitaVendedor.data_visita) == hoje
    ).count()
    
    # Visitas na semana
    visitas_semana = query.filter(
        models.VisitaVendedor.data_visita >= semana_inicio
    ).count()
    
    # Visitas no mês
    visitas_mes = query.filter(
        models.VisitaVendedor.data_visita >= mes_inicio
    ).count()
    
    return {
        'total_visitas': total_visitas,
        'visitas_hoje': visitas_hoje,
        'visitas_semana': visitas_semana,
        'visitas_mes': visitas_mes,
        'visitas_confirmadas': visitas_confirmadas,
        'visitas_pendentes': visitas_pendentes
    }


def delete_visita(
    db: Session,
    visita_id: int,
    empresa_id: int
) -> bool:
    """Remove uma visita (apenas se não confirmada)."""
    visita = get_visita_by_id(db, visita_id, empresa_id)
    
    if not visita:
        return False
    
    # Não permitir remoção de visitas confirmadas
    if visita.confirmada:
        raise ValueError("Não é possível remover uma visita confirmada")
    
    db.delete(visita)
    db.commit()
    
    return True
