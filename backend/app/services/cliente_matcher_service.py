"""
Serviço para matching inteligente e criação automática de clientes a partir de CNPJ.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db import models
from app.utils.cnpj_utils import normalizar_cnpj, validar_cnpj
from app.services.empresa_service import EmpresaService
import logging

logger = logging.getLogger(__name__)


class ClienteMatcherService:
    """Serviço para reconhecimento e criação automática de clientes."""
    
    @staticmethod
    def encontrar_ou_criar_cliente(
        db: Session,
        cnpj: str,
        razao_social: Optional[str] = None,
        endereco: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        empresa_id: Optional[int] = None
    ) -> models.Cliente:
        """
        Encontra cliente existente pelo CNPJ ou cria um novo.
        
        Args:
            db: Sessão do banco de dados
            cnpj: CNPJ do cliente
            razao_social: Razão social do cliente
            endereco: Endereço do cliente
            telefone: Telefone do cliente
            email: Email do cliente
            empresa_id: ID da empresa (obrigatório se não for possível identificar)
            
        Returns:
            Cliente encontrado ou criado
            
        Raises:
            ValueError: Se CNPJ inválido ou empresa_id não fornecido e não identificável
        """
        if not cnpj:
            raise ValueError("CNPJ é obrigatório")
        
        cnpj_normalizado = normalizar_cnpj(cnpj)
        if not cnpj_normalizado or not validar_cnpj(cnpj):
            raise ValueError(f"CNPJ inválido: {cnpj}")
        
        # Se empresa_id não fornecido, tentar identificar pela estrutura existente
        if not empresa_id:
            # Tentar identificar empresa pela empresa vinculada padrão
            # Por padrão, usar HIGIPLAS se não for possível determinar
            empresa_id = EmpresaService.get_empresa_id(db, "HIGIPLAS")
            if not empresa_id:
                raise ValueError("Não foi possível identificar a empresa. empresa_id é obrigatório.")
        
        # Buscar cliente existente pelo CNPJ na empresa correta
        cliente = db.query(models.Cliente).filter(
            models.Cliente.cnpj.isnot(None),
            or_(
                models.Cliente.cnpj == cnpj_normalizado,
                models.Cliente.cnpj == cnpj  # Também busca formatado
            ),
            models.Cliente.empresa_id == empresa_id
        ).first()
        
        if cliente:
            # Atualizar informações se necessário
            atualizado = False
            # Não atualizar com nomes inválidos (ex: "Frete por Conta C")
            if razao_social and ClienteMatcherService._is_nome_cliente_invalido(razao_social):
                razao_social = None
            
            if razao_social and razao_social.strip() and (
                not cliente.razao_social or 
                cliente.razao_social.strip().upper() != razao_social.strip().upper()
            ):
                cliente.razao_social = razao_social.strip()
                atualizado = True
            
            if endereco and endereco.strip() and not cliente.endereco:
                cliente.endereco = endereco.strip()
                atualizado = True
            
            if telefone and telefone.strip() and not cliente.telefone:
                cliente.telefone = telefone.strip()
                atualizado = True
            
            if email and email.strip() and not cliente.email:
                cliente.email = email.strip()
                atualizado = True
            
            # Normalizar CNPJ se diferente
            if cliente.cnpj != cnpj_normalizado:
                cliente.cnpj = cnpj_normalizado
                atualizado = True
            
            if atualizado:
                from datetime import datetime
                cliente.atualizado_em = datetime.now()
                db.commit()
                logger.info(f"Cliente atualizado: {cliente.razao_social} (ID: {cliente.id})")
            
            return cliente
        
        # Criar novo cliente
        # Rejeitar nomes inválidos (ex: "Frete por Conta C" - cabeçalho de tabela)
        if not razao_social or not razao_social.strip() or ClienteMatcherService._is_nome_cliente_invalido(razao_social):
            razao_social = f"Cliente - {cnpj_normalizado}"
        
        # Determinar empresa_vinculada baseado na empresa_id
        empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
        empresa_vinculada = "HIGIPLAS"
        if empresa and "HIGITEC" in empresa.nome.upper():
            empresa_vinculada = "HIGITEC"
        
        novo_cliente = models.Cliente(
            razao_social=razao_social.strip(),
            cnpj=cnpj_normalizado,
            endereco=endereco.strip() if endereco else None,
            telefone=telefone.strip() if telefone else None,
            email=email.strip() if email else None,
            empresa_id=empresa_id,
            empresa_vinculada=empresa_vinculada,
            status_pagamento="BOM_PAGADOR"  # Default
        )
        
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        
        logger.info(f"Cliente criado automaticamente: {novo_cliente.razao_social} (ID: {novo_cliente.id}, CNPJ: {cnpj_normalizado})")
        
        return novo_cliente
    
    @staticmethod
    def buscar_cliente_por_cnpj(
        db: Session,
        cnpj: str,
        empresa_id: Optional[int] = None
    ) -> Optional[models.Cliente]:
        """
        Busca cliente existente apenas pelo CNPJ.
        
        Args:
            db: Sessão do banco de dados
            cnpj: CNPJ do cliente
            empresa_id: ID da empresa para filtrar (opcional)
            
        Returns:
            Cliente encontrado ou None
        """
        cnpj_normalizado = normalizar_cnpj(cnpj)
        if not cnpj_normalizado:
            return None
        
        query = db.query(models.Cliente).filter(
            models.Cliente.cnpj.isnot(None),
            or_(
                models.Cliente.cnpj == cnpj_normalizado,
                models.Cliente.cnpj == cnpj
            )
        )
        
        if empresa_id:
            query = query.filter(models.Cliente.empresa_id == empresa_id)
        
        return query.first()
    
    @staticmethod
    def _is_nome_cliente_invalido(nome: str) -> bool:
        """Rejeita nomes que são cabeçalhos de tabela (ex: 'Frete por Conta C')."""
        if not nome or len(nome) < 3:
            return True
        nome_upper = nome.strip().upper()
        invalidos = (
            "FRETE POR CONTA",
            "9-SEM TRANSPORTE",
            "RAZAO SOCIAL",
        )
        return any(nome_upper == inv or nome_upper.startswith(inv + " ") for inv in invalidos)
    
    @staticmethod
    def extrair_dados_cliente_da_nf(
        texto_nf: str,
        empresa_id: int
    ) -> Dict[str, Any]:
        """
        Extrai dados do cliente a partir do texto da NF.
        
        Args:
            texto_nf: Texto extraído da NF
            empresa_id: ID da empresa emitente
            
        Returns:
            Dicionário com dados do cliente extraídos
        """
        import re
        
        dados = {
            'cnpj': None,
            'razao_social': None,
            'endereco': None,
            'telefone': None,
            'email': None
        }
        
        # Extrair CNPJ do destinatário (para NF de saída)
        # Padrões comuns em NFs
        cnpj_patterns = [
            r'Destinatário[:\s]+[^\n]*CNPJ[:\s]+(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            r'Nome/Razão Social\s+([A-Z][A-Z\s&.-]+?)\s+(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            r'CNPJ[:\s]+(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
        ]
        
        for pattern in cnpj_patterns:
            match = re.search(pattern, texto_nf, re.IGNORECASE | re.MULTILINE)
            if match:
                # Se o padrão tem grupos, tentar extrair razão social e CNPJ
                if len(match.groups()) >= 2:
                    dados['razao_social'] = match.group(1).strip()
                    dados['cnpj'] = match.group(2)
                elif len(match.groups()) == 1:
                    dados['cnpj'] = match.group(1)
                
                if dados['cnpj']:
                    break
        
        # Extrair razão social se não foi extraída com o CNPJ
        if not dados['razao_social']:
            razao_patterns = [
                r'Nome/Razão Social\s+([A-Z][A-Z\s&.-]{5,}?)(?=\s+\d{2}\.\d{3})',
                r'Destinatário[:\s]+([A-Z][A-Z\s&.-]{5,}?)(?=\s+CNPJ)',
                r'Razão Social[:\s]+([A-Z][A-Z\s&.-]{5,})',
            ]
            
            for pattern in razao_patterns:
                match = re.search(pattern, texto_nf, re.IGNORECASE)
                if match:
                    razao = match.group(1).strip()
                    if not ClienteMatcherService._is_nome_cliente_invalido(razao):
                        dados['razao_social'] = razao
                    break
        
        # Validar razao_social extraída com CNPJ - pode ser "Frete por Conta C"
        if dados['razao_social'] and ClienteMatcherService._is_nome_cliente_invalido(dados['razao_social']):
            dados['razao_social'] = None
        
        # Extrair endereço (padrão básico)
        endereco_patterns = [
            r'Endereço[:\s]+([^\n]{10,}?)(?=\n|CEP)',
            r'Logradouro[:\s]+([^\n]{10,})',
        ]
        
        for pattern in endereco_patterns:
            match = re.search(pattern, texto_nf, re.IGNORECASE)
            if match:
                dados['endereco'] = match.group(1).strip()
                break
        
        # Extrair telefone
        telefone_patterns = [
            r'Telefone[:\s]+([\(\)\d\s\-]+)',
            r'Fone[:\s]+([\(\)\d\s\-]+)',
        ]
        
        for pattern in telefone_patterns:
            match = re.search(pattern, texto_nf, re.IGNORECASE)
            if match:
                telefone_limpo = re.sub(r'[^\d]', '', match.group(1))
                if len(telefone_limpo) >= 10:  # Telefone válido tem pelo menos 10 dígitos
                    dados['telefone'] = telefone_limpo
                break
        
        # Extrair email
        email_pattern = r'Email[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(email_pattern, texto_nf, re.IGNORECASE)
        if match:
            dados['email'] = match.group(1).strip()
        
        return dados
