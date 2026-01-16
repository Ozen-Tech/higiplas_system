"""
Utilitários para validação e normalização de CNPJ
"""

import re
from typing import Optional


def normalizar_cnpj(cnpj: str) -> Optional[str]:
    """
    Remove formatação do CNPJ (pontos, barras, hífens, espaços).
    
    Args:
        cnpj: CNPJ com ou sem formatação
        
    Returns:
        CNPJ apenas com números ou None se inválido
    """
    if not cnpj:
        return None
    
    # Remove tudo exceto números
    cnpj_limpo = re.sub(r'[^\d]', '', str(cnpj))
    
    # Valida tamanho (deve ter 14 dígitos)
    if len(cnpj_limpo) != 14:
        return None
    
    return cnpj_limpo


def formatar_cnpj(cnpj: str) -> Optional[str]:
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX.
    
    Args:
        cnpj: CNPJ com ou sem formatação
        
    Returns:
        CNPJ formatado ou None se inválido
    """
    cnpj_limpo = normalizar_cnpj(cnpj)
    if not cnpj_limpo:
        return None
    
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando algoritmo de validação.
    
    Args:
        cnpj: CNPJ para validar
        
    Returns:
        True se CNPJ é válido, False caso contrário
    """
    cnpj_limpo = normalizar_cnpj(cnpj)
    if not cnpj_limpo:
        return False
    
    # Verifica se todos os dígitos são iguais (CNPJ inválido)
    if len(set(cnpj_limpo)) == 1:
        return False
    
    # Validação dos dígitos verificadores
    def calcular_digito(cnpj: str, posicoes: list) -> int:
        soma = 0
        for i, pos in enumerate(posicoes):
            soma += int(cnpj[i]) * pos
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito verificador
    posicoes_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito_1 = calcular_digito(cnpj_limpo[:12], posicoes_1)
    
    if digito_1 != int(cnpj_limpo[12]):
        return False
    
    # Segundo dígito verificador
    posicoes_2 = [6] + posicoes_1
    digito_2 = calcular_digito(cnpj_limpo[:13], posicoes_2)
    
    return digito_2 == int(cnpj_limpo[13])


def extrair_cnpj_texto(texto: str) -> list[str]:
    """
    Extrai todos os CNPJs encontrados em um texto.
    
    Args:
        texto: Texto para buscar CNPJs
        
    Returns:
        Lista de CNPJs encontrados (normalizados)
    """
    # Padrão para CNPJ formatado: XX.XXX.XXX/XXXX-XX
    padrao_formatado = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
    
    # Padrão para CNPJ não formatado (14 dígitos consecutivos)
    padrao_simples = r'\d{14}'
    
    cnpjs_encontrados = []
    
    # Buscar CNPJs formatados
    for match in re.finditer(padrao_formatado, texto):
        cnpj = normalizar_cnpj(match.group())
        if cnpj and cnpj not in cnpjs_encontrados:
            cnpjs_encontrados.append(cnpj)
    
    # Buscar CNPJs não formatados (evitar falsos positivos)
    # Apenas se não for parte de um CNPJ formatado já encontrado
    texto_sem_formatados = re.sub(padrao_formatado, '', texto)
    for match in re.finditer(padrao_simples, texto_sem_formatados):
        cnpj = match.group()
        # Validar que não é apenas uma sequência aleatória
        if len(set(cnpj)) > 1:  # Não são todos dígitos iguais
            if cnpj not in cnpjs_encontrados:
                cnpjs_encontrados.append(cnpj)
    
    return cnpjs_encontrados
