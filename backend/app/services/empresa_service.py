"""
Serviço para identificação e gerenciamento de empresas por CNPJ.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.db import models
from app.utils.cnpj_utils import normalizar_cnpj, validar_cnpj


class EmpresaService:
    """Serviço centralizado para identificação de empresas."""
    
    # CNPJs das empresas
    HIGIPLAS_CNPJ_FORMATADO = "22.599.389/0001-76"
    HIGIPLAS_CNPJ_NORMALIZADO = "22599389000176"
    HIGITEC_CNPJ_FORMATADO = "44.874.126/0001-60"
    HIGITEC_CNPJ_NORMALIZADO = "44874126000160"
    
    @staticmethod
    def identificar_empresa_por_cnpj(db: Session, cnpj: str) -> Optional[int]:
        """
        Identifica a empresa pelo CNPJ fornecido.
        
        Args:
            db: Sessão do banco de dados
            cnpj: CNPJ formatado ou não formatado
            
        Returns:
            empresa_id se encontrado, None caso contrário
        """
        cnpj_normalizado = normalizar_cnpj(cnpj)
        if not cnpj_normalizado:
            return None
        
        # Verificação direta pelos CNPJs conhecidos
        if cnpj_normalizado == EmpresaService.HIGIPLAS_CNPJ_NORMALIZADO:
            return EmpresaService.get_empresa_id(db, "HIGIPLAS")
        
        if cnpj_normalizado == EmpresaService.HIGITEC_CNPJ_NORMALIZADO:
            return EmpresaService.get_empresa_id(db, "HIGITEC")
        
        # Buscar no banco de dados por CNPJ
        empresa = db.query(models.Empresa).filter(
            models.Empresa.cnpj.isnot(None)
        ).all()
        
        for emp in empresa:
            if normalizar_cnpj(emp.cnpj) == cnpj_normalizado:
                return emp.id
        
        return None
    
    @staticmethod
    def get_empresa_id(db: Session, nome_empresa: str) -> Optional[int]:
        """
        Obtém o ID da empresa pelo nome.
        
        Args:
            db: Sessão do banco de dados
            nome_empresa: Nome da empresa (HIGIPLAS ou HIGITEC)
            
        Returns:
            empresa_id se encontrado, None caso contrário
        """
        nome_upper = nome_empresa.upper().strip()
        
        empresa = db.query(models.Empresa).filter(
            models.Empresa.nome.ilike(f"%{nome_upper}%")
        ).first()
        
        if empresa:
            return empresa.id
        
        return None
    
    @staticmethod
    def get_empresa_cnpj(db: Session, empresa_id: int) -> Optional[str]:
        """
        Obtém o CNPJ formatado da empresa.
        
        Args:
            db: Sessão do banco de dados
            empresa_id: ID da empresa
            
        Returns:
            CNPJ formatado ou None
        """
        empresa = db.query(models.Empresa).filter(
            models.Empresa.id == empresa_id
        ).first()
        
        if empresa and empresa.cnpj:
            return empresa.cnpj
        
        return None
    
    @staticmethod
    def garantir_empresas_existem(db: Session) -> dict[str, int]:
        """
        Garante que as empresas HIGIPLAS e HIGITEC existem no banco.
        Cria se não existirem.
        
        Args:
            db: Sessão do banco de dados
            
        Returns:
            Dicionário com {nome_empresa: empresa_id}
        """
        empresas = {}
        
        # Criar/verificar HIGIPLAS
        empresa_higiplas = db.query(models.Empresa).filter(
            models.Empresa.nome.ilike("%HIGIPLAS%")
        ).first()
        
        if not empresa_higiplas:
            empresa_higiplas = models.Empresa(
                nome="HIGIPLAS",
                cnpj=EmpresaService.HIGIPLAS_CNPJ_FORMATADO
            )
            db.add(empresa_higiplas)
            db.flush()
        
        empresas["HIGIPLAS"] = empresa_higiplas.id
        
        # Criar/verificar HIGITEC
        empresa_higitec = db.query(models.Empresa).filter(
            models.Empresa.nome.ilike("%HIGITEC%")
        ).first()
        
        if not empresa_higitec:
            empresa_higitec = models.Empresa(
                nome="HIGITEC",
                cnpj=EmpresaService.HIGITEC_CNPJ_FORMATADO
            )
            db.add(empresa_higitec)
            db.flush()
        
        empresas["HIGITEC"] = empresa_higitec.id
        
        db.commit()
        
        return empresas
    
    @staticmethod
    def identificar_tipo_nf_por_cnpj(cnpj: str) -> Optional[str]:
        """
        Identifica o tipo de NF (ENTRADA ou SAIDA) baseado no CNPJ.
        Se o CNPJ for da HIGIPLAS ou HIGITEC, é uma NF de SAÍDA (venda).
        Caso contrário, pode ser uma NF de ENTRADA (compra).
        
        Args:
            cnpj: CNPJ a verificar
            
        Returns:
            'SAIDA' se CNPJ for da empresa, None caso contrário (será verificado pelo nome do arquivo/contexto)
        """
        cnpj_normalizado = normalizar_cnpj(cnpj)
        if not cnpj_normalizado:
            return None
        
        if (cnpj_normalizado == EmpresaService.HIGIPLAS_CNPJ_NORMALIZADO or
            cnpj_normalizado == EmpresaService.HIGITEC_CNPJ_NORMALIZADO):
            return "SAIDA"
        
        return None
