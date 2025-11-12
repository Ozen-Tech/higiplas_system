"""
Validadores centralizados para regras de negócio.

Fornece validadores reutilizáveis para orçamentos, estoque, permissões e transições de status.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..db import models
from ..core.exceptions import (
    NotFoundError,
    OrcamentoStatusError,
    StockInsufficientError,
    BusinessRuleException,
    PermissionDeniedError
)
from ..core.constants import (
    OrcamentoStatus,
    STATUS_CONFIRMAVEL,
    TipoMovimentacao
)


class OrcamentoValidator:
    """Validador para operações com orçamentos."""
    
    @staticmethod
    def validar_orcamento_existe(
        db: Session,
        orcamento_id: int
    ) -> models.Orcamento:
        """
        Valida se o orçamento existe no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            orcamento_id: ID do orçamento
            
        Returns:
            O orçamento encontrado
            
        Raises:
            NotFoundError: Se o orçamento não for encontrado
        """
        from ..crud import orcamento as crud_orcamento
        
        orcamento = crud_orcamento.get_orcamento_by_id(db, orcamento_id)
        if not orcamento:
            raise NotFoundError("Orçamento", orcamento_id)
        return orcamento
    
    @staticmethod
    def validar_status_confirmacao(
        orcamento: models.Orcamento
    ) -> None:
        """
        Valida se o orçamento está em um status que permite confirmação.
        
        Args:
            orcamento: O orçamento a ser validado
            
        Raises:
            OrcamentoStatusError: Se o status não permitir confirmação
        """
        if orcamento.status not in STATUS_CONFIRMAVEL:
            raise OrcamentoStatusError(
                orcamento_id=orcamento.id,
                status_atual=orcamento.status,
                operacao="confirmado",
                status_validos=STATUS_CONFIRMAVEL
            )
    
    @staticmethod
    def validar_status_transicao(
        status_atual: str,
        novo_status: str,
        transicoes_validas: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """
        Valida se uma transição de status é permitida.
        
        Args:
            status_atual: Status atual do orçamento
            novo_status: Novo status desejado
            transicoes_validas: Dicionário com transições permitidas (opcional)
            
        Raises:
            OrcamentoStatusError: Se a transição não for permitida
        """
        # Se não especificado, permite qualquer transição entre status válidos
        if transicoes_validas is None:
            status_validos = [s.value for s in OrcamentoStatus]
            if novo_status not in status_validos:
                raise OrcamentoStatusError(
                    orcamento_id=0,  # Não temos ID aqui
                    status_atual=status_atual,
                    operacao=f"alterado para '{novo_status}'",
                    status_validos=status_validos
                )
        else:
            if status_atual not in transicoes_validas:
                raise OrcamentoStatusError(
                    orcamento_id=0,
                    status_atual=status_atual,
                    operacao=f"alterado para '{novo_status}'",
                    status_validos=list(transicoes_validas.keys())
                )
            if novo_status not in transicoes_validas[status_atual]:
                raise OrcamentoStatusError(
                    orcamento_id=0,
                    status_atual=status_atual,
                    operacao=f"alterado para '{novo_status}'",
                    status_validos=transicoes_validas[status_atual]
                )


class StockValidator:
    """Validador para operações de estoque."""
    
    @staticmethod
    def validar_produto_existe(
        db: Session,
        produto_id: int,
        empresa_id: int
    ) -> models.Produto:
        """
        Valida se o produto existe e pertence à empresa.
        
        Args:
            db: Sessão do banco de dados
            produto_id: ID do produto
            empresa_id: ID da empresa
            
        Returns:
            O produto encontrado
            
        Raises:
            NotFoundError: Se o produto não for encontrado
        """
        produto = db.query(models.Produto).filter(
            models.Produto.id == produto_id,
            models.Produto.empresa_id == empresa_id
        ).first()
        
        if not produto:
            raise NotFoundError("Produto", produto_id)
        return produto
    
    @staticmethod
    def validar_estoque_disponivel(
        produto: models.Produto,
        quantidade_solicitada: float
    ) -> None:
        """
        Valida se há estoque suficiente para a quantidade solicitada.
        
        Args:
            produto: O produto a ser validado
            quantidade_solicitada: Quantidade desejada
            
        Raises:
            StockInsufficientError: Se o estoque for insuficiente
        """
        if produto.quantidade_em_estoque < quantidade_solicitada:
            raise StockInsufficientError(
                produto_nome=produto.nome,
                quantidade_disponivel=produto.quantidade_em_estoque,
                quantidade_solicitada=quantidade_solicitada
            )
    
    @staticmethod
    def validar_estoque_orcamento(
        db: Session,
        orcamento: models.Orcamento
    ) -> List[Dict[str, Any]]:
        """
        Valida o estoque disponível para todos os itens de um orçamento.
        
        Args:
            db: Sessão do banco de dados
            orcamento: O orçamento a ser validado
            
        Returns:
            Lista vazia se tudo estiver OK
            
        Raises:
            BusinessRuleException: Se houver produtos com estoque insuficiente
        """
        produtos_insuficientes = []
        
        for item in orcamento.itens:
            produto = item.produto
            if produto.quantidade_em_estoque < item.quantidade:
                produtos_insuficientes.append({
                    'produto': produto.nome,
                    'produto_id': produto.id,
                    'disponivel': produto.quantidade_em_estoque,
                    'solicitado': item.quantidade
                })
        
        if produtos_insuficientes:
            detalhes = ", ".join([
                f"{p['produto']} (disponível: {p['disponivel']}, solicitado: {p['solicitado']})"
                for p in produtos_insuficientes
            ])
            raise BusinessRuleException(
                f"Estoque insuficiente para os seguintes produtos: {detalhes}"
            )
        
        return produtos_insuficientes


class PermissionValidator:
    """Validador para permissões de usuário."""
    
    @staticmethod
    def validar_admin(
        usuario: models.Usuario,
        admin_email: str = "enzo.alverde@gmail.com"
    ) -> None:
        """
        Valida se o usuário é administrador.
        
        Args:
            usuario: O usuário a ser validado
            admin_email: Email do administrador (padrão)
            
        Raises:
            PermissionDeniedError: Se o usuário não for admin
        """
        if usuario.email.lower() != admin_email.lower():
            raise PermissionDeniedError(
                "Acesso negado. Apenas o administrador pode acessar este recurso."
            )
    
    @staticmethod
    def validar_proprietario_ou_admin(
        usuario: models.Usuario,
        recurso_usuario_id: int,
        admin_email: str = "enzo.alverde@gmail.com"
    ) -> None:
        """
        Valida se o usuário é o proprietário do recurso ou administrador.
        
        Args:
            usuario: O usuário a ser validado
            recurso_usuario_id: ID do usuário proprietário do recurso
            admin_email: Email do administrador (padrão)
            
        Raises:
            PermissionDeniedError: Se o usuário não tiver permissão
        """
        is_admin = usuario.email.lower() == admin_email.lower()
        is_owner = usuario.id == recurso_usuario_id
        
        if not (is_admin or is_owner):
            raise PermissionDeniedError(
                "Você não tem permissão para acessar este recurso."
            )


class StatusTransitionValidator:
    """Validador para transições de status."""
    
    @staticmethod
    def validar_transicao_orcamento(
        status_atual: str,
        novo_status: str
    ) -> None:
        """
        Valida transição de status de orçamento.
        
        Args:
            status_atual: Status atual
            novo_status: Novo status desejado
            
        Raises:
            OrcamentoStatusError: Se a transição não for válida
        """
        OrcamentoValidator.validar_status_transicao(
            status_atual=status_atual,
            novo_status=novo_status
        )

