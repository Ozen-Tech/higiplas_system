import re
from typing import List, Dict, Any

def extrair_produtos_inteligente_entrada_melhorado(texto_completo: str) -> List[Dict[str, Any]]:
    """Extração inteligente de produtos para PDFs de entrada - Versão melhorada com logs detalhados."""
    
    produtos = []
    linhas = texto_completo.split('\n')
    
    print(f"DEBUG: Total de linhas no PDF: {len(linhas)}")
    
    # Indicadores específicos para GIRASSOL
    indicadores_produtos = [
        'DADOS DOS PRODUTOS / SERVIÇOS',
        'DADOS DOS PRODUTOS',
        'Dados dos Produtos',
        'Produtos e Serviços',
        'CÓDIGO VALOR VALOR BASE CÁLCULO',
        'DESCRIÇÃO DO PRODUTO/SERVIÇO'
    ]
    
    # Indicadores de fim específicos para GIRASSOL
    indicadores_fim = [
        'DADOS ADICIONAIS',
        'Dados Adicionais',
        'Informações Complementares',
        'INFORMAÇÕES COMPLEMENTARES',
        'Observações',
        'Total da Nota',
        'Valor Total'
    ]
    
    inicio_produtos = False
    fim_secao = False
    linha_inicio = -1
    linha_fim = -1
    
    # Primeira passada: encontrar seção de produtos
    for i, linha in enumerate(linhas):
        # Verificar se chegamos ao início da seção de produtos
        if not inicio_produtos:
            for indicador in indicadores_produtos:
                if indicador in linha:
                    inicio_produtos = True
                    linha_inicio = i
                    print(f"DEBUG: Seção de produtos iniciada na linha {i}: {indicador}")
                    break
            continue
        
        # Verificar se chegamos ao fim da seção de produtos
        for indicador in indicadores_fim:
            if indicador in linha:
                fim_secao = True
                linha_fim = i
                print(f"DEBUG: Seção de produtos finalizada na linha {i}: {indicador}")
                break
        
        if fim_secao:
            break
    
    if not inicio_produtos:
        print("DEBUG: Seção de produtos não encontrada. Tentando buscar em todo o texto...")
        linha_inicio = 0
        linha_fim = len(linhas)
    
    print(f"DEBUG: Processando linhas {linha_inicio} a {linha_fim}")
    
    # Segunda passada: extrair produtos
    for i in range(linha_inicio, linha_fim if linha_fim > 0 else len(linhas)):
        if i >= len(linhas):
            break
            
        linha = linhas[i]
        linha_limpa = linha.strip()
        
        # Pular linhas vazias ou muito curtas
        if not linha_limpa or len(linha_limpa) < 5:
            continue
        
        # Log de linhas com potencial de serem produtos
        if any(char.isdigit() for char in linha_limpa[:10]):  # Se começa com números
            print(f"DEBUG: Linha {i} candidata: '{linha_limpa[:80]}...'")
        
        # Padrões mais flexíveis para diferentes formatos de PDF
        padroes_produto = [
            # Padrão 1: Código de 4+ dígitos + descrição + 3 valores numéricos
            r'^(\d{4,})\s+([A-Za-z][A-Za-z\s/\-()0-9.,]+?)\s+(\d+[,.]?\d*)\s+([\d,]+[,.]\d*)\s+([\d,]+[,.]\d*)',
            # Padrão 2: Código + descrição com NCM, CST, CFOP (formato GIRASSOL)
            r'^(\d{4,})\s+([A-Za-z][A-Za-z\s/\-()0-9.,]+?)\s+(\d{8})\s+(\d{3})\s+(\d{4})\s+(\w+)\s+(\d+[,.]?\d*)\s+([\d,]+[,.]\d*)\s+([\d,]+[,.]\d*)',
            # Padrão 3: Busca mais flexível por código e valores
            r'(\d{4,})\s+(.+?)\s+(\d+[,.]?\d*)\s+([\d,]+[,.]\d*)\s+([\d,]+[,.]\d*)$',
            # Padrão 4: Código seguido de texto e pelo menos 2 valores
            r'(\d{4,})\s+([A-Za-z].+?)\s+(\d+[,.]?\d*)\s+([\d,]+[,.]\d*)',
            # Padrão 5: Busca por qualquer linha com código e múltiplos valores
            r'(\d{4,}).*?([A-Za-z][A-Za-z\s/\-()0-9.,]{5,}?).*?(\d+[,.]?\d*).*?([\d,]+[,.]\d*).*?([\d,]+[,.]\d*)',
        ]
        
        produto_encontrado = False
        
        for j, padrao in enumerate(padroes_produto):
            try:
                produto_match = re.search(padrao, linha_limpa)
                
                if produto_match:
                    print(f"DEBUG: MATCH! Padrão {j} na linha {i}:")
                    print(f"DEBUG: Grupos encontrados: {produto_match.groups()}")
                    
                    # Extrair dados baseado no padrão
                    grupos = produto_match.groups()
                    
                    if len(grupos) >= 4:  # Pelo menos código, descrição, quantidade, valor
                        codigo = grupos[0]
                        descricao = grupos[1].strip()
                        
                        # Determinar posições dos valores baseado no número de grupos
                        if len(grupos) == 9:  # Padrão completo com NCM, CST, CFOP
                            quantidade = float(grupos[6].replace(',', '.'))
                            valor_unitario = float(grupos[7].replace(',', '.'))
                            valor_total = float(grupos[8].replace(',', '.'))
                        elif len(grupos) >= 5:  # Padrão com 3 valores
                            quantidade = float(grupos[2].replace(',', '.'))
                            valor_unitario = float(grupos[3].replace(',', '.'))
                            valor_total = float(grupos[4].replace(',', '.'))
                        else:  # Padrão com 2 valores
                            quantidade = float(grupos[2].replace(',', '.'))
                            valor_unitario = float(grupos[3].replace(',', '.'))
                            valor_total = quantidade * valor_unitario
                        
                        produto = {
                            'item': len(produtos) + 1,
                            'codigo': codigo,
                            'descricao': descricao,
                            'quantidade': quantidade,
                            'valor_unitario': valor_unitario,
                            'valor_total': valor_total
                        }
                        
                        produtos.append(produto)
                        produto_encontrado = True
                        
                        print(f"DEBUG: Produto extraído: {produto}")
                        break
                        
            except Exception as e:
                print(f"DEBUG: Erro ao processar padrão {j}: {e}")
                continue
        
        if not produto_encontrado and any(char.isdigit() for char in linha_limpa[:10]):
            print(f"DEBUG: Linha {i} não matched por nenhum padrão: '{linha_limpa}'")
    
    print(f"DEBUG: Total de produtos extraídos: {len(produtos)}")
    return produtos

# Função para testar a extração
def testar_extracao_com_texto(texto: str):
    """Função para testar a extração com um texto específico."""
    print("=== INICIANDO TESTE DE EXTRAÇÃO ===")
    produtos = extrair_produtos_inteligente_entrada_melhorado(texto)
    print(f"\n=== RESULTADO: {len(produtos)} produtos encontrados ===")
    for produto in produtos:
        print(f"- {produto}")
    return produtos