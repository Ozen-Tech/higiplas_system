from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..services.stock_report_service import StockReportService
from ..core.logger import stock_operations_logger

router = APIRouter(
    prefix="/reports",
    tags=["Relatórios"]
)

@router.get(
    "/stock/weekly",
    summary="Relatório Semanal de Estoque",
    description="Gera um relatório detalhado de todas as movimentações de estoque dos últimos 7 dias (ou período customizado)"
)
def get_weekly_stock_report(
    start_date: Optional[str] = Query(None, description="Data inicial no formato YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Data final no formato YYYY-MM-DD"),
    format: str = Query("json", description="Formato de exportação: json, pdf, xlsx"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    try:
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data inicial inválido. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data final inválido. Use YYYY-MM-DD")
        
        if format not in ["json", "pdf", "xlsx"]:
            raise HTTPException(status_code=400, detail="Formato inválido. Use: json, pdf ou xlsx")
        
        report = StockReportService.generate_weekly_stock_report(
            db=db,
            empresa_id=current_user.empresa_id,
            start_date=start_dt,
            end_date=end_dt,
            format=format
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        stock_operations_logger.error(f"[weeklyStockReport] ERROR - usuario_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get(
    "/stock/monthly",
    summary="Relatório Mensal de Estoque",
    description="Gera um relatório detalhado de todas as movimentações de estoque do último mês"
)
def get_monthly_stock_report(
    month: Optional[int] = Query(None, description="Mês (1-12)"),
    year: Optional[int] = Query(None, description="Ano (ex: 2025)"),
    format: str = Query("json", description="Formato de exportação: json, pdf, xlsx"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    try:
        now = datetime.now()
        
        if not year:
            year = now.year
        if not month:
            month = now.month
        
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Mês deve estar entre 1 e 12")
        
        if month == 12:
            start_dt = datetime(year, month, 1)
            end_dt = datetime(year + 1, 1, 1)
        else:
            start_dt = datetime(year, month, 1)
            end_dt = datetime(year, month + 1, 1)
        
        if format not in ["json", "pdf", "xlsx"]:
            raise HTTPException(status_code=400, detail="Formato inválido. Use: json, pdf ou xlsx")
        
        report = StockReportService.generate_weekly_stock_report(
            db=db,
            empresa_id=current_user.empresa_id,
            start_date=start_dt,
            end_date=end_dt,
            format=format
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        stock_operations_logger.error(f"[monthlyStockReport] ERROR - usuario_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get(
    "/stock/custom",
    summary="Relatório Customizado de Estoque",
    description="Gera um relatório de estoque para um período específico"
)
def get_custom_stock_report(
    start_date: str = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    end_date: str = Query(..., description="Data final no formato YYYY-MM-DD"),
    format: str = Query("json", description="Formato de exportação: json, pdf, xlsx"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    try:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="Data inicial não pode ser maior que data final")
        
        if format not in ["json", "pdf", "xlsx"]:
            raise HTTPException(status_code=400, detail="Formato inválido. Use: json, pdf ou xlsx")
        
        report = StockReportService.generate_weekly_stock_report(
            db=db,
            empresa_id=current_user.empresa_id,
            start_date=start_dt,
            end_date=end_dt,
            format=format
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        stock_operations_logger.error(f"[customStockReport] ERROR - usuario_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")
