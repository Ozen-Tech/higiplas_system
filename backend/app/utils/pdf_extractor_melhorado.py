import re
from typing import List, Dict, Any

def extrair_produtos_inteligente_entrada_melhorado(texto_completo: str) -> List[Dict[str, Any]]:
    """Extração inteligente de produtos para PDFs de entrada - Versão melhorada com logs detalhados."""
    
    produtos = []
    linhas = texto_completo.split('\n')
    
    print(f"DEBUG: Total de linhas no PDF: {len(linhas)}")
    
    # Primeiro, tentar detectar o formato específico do PDF (ex: CIRCUS)
    # Padrão: ITEM CÓDIGO DESCRIÇÃO NCM CST CFOP UN QTD VALOR_UNIT ... VALOR_TOTAL
    padrao_circus = re.compile(
        r'^(\d+)\s+'      # Item
        r'(\d+)\s+'       # Código
        r'(.+?)\s+'       # Descrição (captura tudo até o próximo espaço + números)
        r'(\d{8})\s+'     # NCM (8 dígitos)
        r'(\d{4})\s+'     # CST (4 dígitos)
        r'(\d{4})\s+'     # CFOP (4 dígitos)
        r'(\w+)\s+'       # Unidade
        r'([\d,]+)\s+'    # Quantidade
        r'([\d,]+)\s+'    # Valor unitário
        r'.*?([\d,]+)\s+' # Valor total
        r'.*$'            # Resto da linha
    )
    
    print("DEBUG: Tentando extrair produtos com padrão CIRCUS...")
    
    # Padrão específico para PDFs do tipo "CIRCUS" - formato real observado
    padrao_circus_especifico = re.compile(
        r'^(.+?)\s+'           # Descrição do produto
        r'(\d{3})\s+'          # Código do produto (3 dígitos)
        r'(\d{8})\s+'          # NCM (8 dígitos)
        r'(\d{4})\s+'          # CST (4 dígitos)
        r'(\d{4})\s+'          # CFOP (4 dígitos)
        r'(UN)\s+'             # Unidade
        r'([\d,]+)\s+'         # Quantidade
        r'([\d,]+)\s+'         # Valor unitário
        r'([\d,]+)\s+'         # Valor total
        r'.*$'                 # Resto da linha (impostos, etc.)
    )
    
    # Primeiro, identificar linhas que contêm produtos
    linhas_produtos = []
    for linha in linhas:
        linha_limpa = linha.strip()
        if re.search(r'\b\d{3}\s+\d{8}\s+\d{4}\s+\d{4}\s+UN\s+', linha_limpa):
            linhas_produtos.append(linha_limpa)
    
    # Processar as linhas de produtos identificadas
    for i, linha in enumerate(linhas_produtos):
        match = padrao_circus_especifico.match(linha)
        if match:
            try:
                descricao = match.group(1).strip()
                codigo = match.group(2)
                ncm = match.group(3)
                cst = match.group(4)
                cfop = match.group(5)
                unidade = match.group(6)
                quantidade_str = match.group(7).replace(',', '.')
                valor_unitario_str = match.group(8).replace(',', '.')
                valor_total_str = match.group(9).replace(',', '.')
                
                quantidade = float(quantidade_str)
                valor_unitario = float(valor_unitario_str)
                valor_total = float(valor_total_str)
                
                produto = {
                    'item': len(produtos) + 1,
                    'codigo': codigo,
                    'descricao': descricao,
                    'ncm': ncm,
                    'cst': cst,
                    'cfop': cfop,
                    'unidade': unidade,
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_total
                }
                
                produtos.append(produto)
                print(f"DEBUG: Produto CIRCUS extraído - Item {len(produtos)}: {codigo} - {descricao} - Qtd: {quantidade}")
                
            except (ValueError, IndexError) as e:
                print(f"DEBUG: Erro ao processar linha CIRCUS {i}: {linha} - Erro: {e}")
                continue
    
    # Se encontrou produtos com padrão CIRCUS, retornar
    if produtos:
        print(f"DEBUG: Extração CIRCUS concluída. {len(produtos)} produtos encontrados.")
        return produtos
    
    print("DEBUG: Padrão CIRCUS não encontrado. Tentando padrão GIRASSOL...")
    
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