"""
Funções utilitárias reutilizáveis.

Fornece helpers para operações comuns como formatação,
validação, parsing e cálculos seguros.
"""

from typing import Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Realiza divisão segura, evitando divisão por zero.
    
    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor padrão se divisão por zero (padrão: 0.0)
        
    Returns:
        Resultado da divisão ou valor padrão
    """
    if denominator == 0:
        return default
    return numerator / denominator


def format_currency(value: float, currency: str = "R$") -> str:
    """
    Formata um valor como moeda.
    
    Args:
        value: Valor a ser formatado
        currency: Símbolo da moeda (padrão: "R$")
        
    Returns:
        String formatada (ex: "R$ 1.234,56")
    """
    return f"{currency} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_date(date_string: str, format: str = "%Y-%m-%d") -> Optional[date]:
    """
    Faz parsing seguro de uma string de data.
    
    Args:
        date_string: String com a data
        format: Formato esperado (padrão: "%Y-%m-%d")
        
    Returns:
        Objeto date ou None se inválido
    """
    try:
        return datetime.strptime(date_string, format).date()
    except (ValueError, TypeError):
        return None


def parse_datetime(datetime_string: str, format: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Faz parsing seguro de uma string de datetime.
    
    Args:
        datetime_string: String com o datetime
        format: Formato esperado (padrão: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        Objeto datetime ou None se inválido
    """
    try:
        return datetime.strptime(datetime_string, format)
    except (ValueError, TypeError):
        return None


def parse_float(value: Union[str, int, float], default: float = 0.0) -> float:
    """
    Faz parsing seguro de um valor para float.
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se conversão falhar
        
    Returns:
        Float ou valor padrão
    """
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove espaços e caracteres não numéricos (exceto ponto e vírgula)
            cleaned = value.strip().replace(",", ".")
            return float(cleaned)
        return default
    except (ValueError, TypeError):
        return default


def parse_int(value: Union[str, int, float], default: int = 0) -> int:
    """
    Faz parsing seguro de um valor para int.
    
    Args:
        value: Valor a ser convertido
        default: Valor padrão se conversão falhar
        
    Returns:
        Int ou valor padrão
    """
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            # Remove espaços e caracteres não numéricos
            cleaned = value.strip().replace(",", "").replace(".", "")
            return int(cleaned)
        return default
    except (ValueError, TypeError):
        return default


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza input de texto, removendo caracteres perigosos.
    
    Args:
        text: Texto a ser sanitizado
        max_length: Comprimento máximo (None = sem limite)
        
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
    
    # Remove caracteres de controle e espaços extras
    sanitized = " ".join(text.split())
    
    # Limita comprimento se especificado
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca texto se exceder o comprimento máximo.
    
    Args:
        text: Texto a ser truncado
        max_length: Comprimento máximo
        suffix: Sufixo a adicionar se truncado (padrão: "...")
        
    Returns:
        Texto truncado se necessário
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def calculate_percentage(part: float, total: float, decimals: int = 2) -> float:
    """
    Calcula porcentagem de forma segura.
    
    Args:
        part: Parte
        total: Total
        decimals: Casas decimais (padrão: 2)
        
    Returns:
        Porcentagem (0-100)
    """
    if total == 0:
        return 0.0
    
    percentage = (part / total) * 100
    return round(percentage, decimals)


def round_currency(value: float, decimals: int = 2) -> float:
    """
    Arredonda valor monetário.
    
    Args:
        value: Valor a ser arredondado
        decimals: Casas decimais (padrão: 2)
        
    Returns:
        Valor arredondado
    """
    return round(value, decimals)

