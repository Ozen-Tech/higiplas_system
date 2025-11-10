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
    
    # Indicadores específicos para GIRASSOL (usados apenas para otimização, não para limitar)
    indicadores_produtos = [
        'DADOS DOS PRODUTOS / SERVIÇOS',
        'DADOS DOS PRODUTOS',
        'Dados dos Produtos',
        'Produtos e Serviços',
        'CÓDIGO VALOR VALOR BASE CÁLCULO',
        'DESCRIÇÃO DO PRODUTO/SERVIÇO'
    ]
    
    # Encontrar a primeira linha onde produtos começam (para otimização)
    linha_inicio = 0
    for i, linha in enumerate(linhas):
        for indicador in indicadores_produtos:
            if indicador in linha:
                linha_inicio = i
                print(f"DEBUG: Seção de produtos iniciada na linha {i}: {indicador}")
                break
        if linha_inicio > 0:
            break
    
    # IMPORTANTE: Processar TODAS as linhas do texto, não apenas até um indicador de fim
    # Isso garante que produtos em múltiplas páginas sejam processados
    linha_fim = len(linhas)
    
    print(f"DEBUG: Processando linhas {linha_inicio} a {linha_fim} (todas as linhas do PDF)")
    
    # Padrão GIRASSOL onde o código do produto vem colado à descrição (sem espaço)
    # Exemplo de linha real:
    # 1005805AGUASSANI BB 5L 28289011 000 6101 UN 112       18,30      2.049,60      2.049,60    143,47 7
    padrao_girassol_compacto = re.compile(
        r'^(\d{5,})\s*'                               # Código do produto (5+ dígitos)
        r'([A-Z][A-Z0-9\s\./()\-]{3,}?)\s+'          # Descrição (maiúsculas, números e símbolos usuais)
        r'(\d{8})\s+'                                  # NCM (8 dígitos)
        r'(\d{3})\s+'                                  # CST (3 dígitos)
        r'(\d{4})\s+'                                  # CFOP (4 dígitos)
        r'([A-Z]{2,})\s+'                               # Unidade (UN, CX, etc.)
        r'([\d\.]+,[\d]{0,3}|\d+)\s+'               # Quantidade (com ou sem decimais)
        r'([\d\.]+,[\d]{2})\s+'                       # Valor unitário
        r'([\d\.]+,[\d]{2})'                           # Valor total
    )
    
    # Palavras-chave que indicam que a linha NÃO é um produto
    palavras_excluir = [
        'TOTAL', 'TOTAIS', 'SUBTOTAL', 'SUBTOTAIS',
        'ICMS', 'IPI', 'PIS', 'COFINS', 'IMPOSTO', 'IMPOSTOS',
        'DESCONTO', 'DESCONTOS', 'ACRESCIMO', 'ACRESCIMOS',
        'FRETE', 'SEGURO', 'OUTRAS DESPESAS',
        'BASE DE CALCULO', 'VALOR DO ICMS', 'VALOR DO IPI',
        'DADOS ADICIONAIS', 'INFORMACOES COMPLEMENTARES',
        'OBSERVACOES', 'OBSERVACAO'
    ]
    
    # Códigos já processados para evitar duplicatas
    codigos_processados = set()
    
    # Segunda passada: extrair produtos de TODAS as linhas do PDF
    # Processa todas as linhas para garantir que produtos em múltiplas páginas sejam capturados
    for i in range(linha_inicio, linha_fim):
        if i >= len(linhas):
            break
            
        linha = linhas[i]
        linha_limpa = linha.strip()
        
        # Pular linhas vazias ou muito curtas
        if not linha_limpa or len(linha_limpa) < 5:
            continue
        
        # Filtrar linhas que claramente não são produtos
        linha_upper = linha_limpa.upper()
        if any(palavra in linha_upper for palavra in palavras_excluir):
            continue
        
        # Pular linhas que começam com palavras que indicam totais/impostos
        if any(linha_upper.startswith(palavra) for palavra in ['TOTAL', 'SUBTOTAL', 'ICMS', 'IPI', 'PIS', 'COFINS']):
            continue
        
        # Log de linhas com potencial de serem produtos
        if any(char.isdigit() for char in linha_limpa[:10]):  # Se começa com números
            print(f"DEBUG: Linha {i} candidata: '{linha_limpa[:80]}...'")
        
        # 1) Tentar primeiro o padrão GIRASSOL compacto (código colado na descrição)
        try:
            mg = padrao_girassol_compacto.search(linha_limpa)
            if mg:
                codigo = mg.group(1)
                descricao = mg.group(2).strip()
                unidade = mg.group(6)
                # Converter números no formato PT-BR
                def _ptbr_to_float(s: str) -> float:
                    return float(s.replace('.', '').replace(',', '.'))
                quantidade = _ptbr_to_float(mg.group(7))
                valor_unitario = _ptbr_to_float(mg.group(8))
                valor_total = _ptbr_to_float(mg.group(9))
                
                # Validar se não é duplicata e se os valores fazem sentido
                if codigo in codigos_processados:
                    print(f"DEBUG: Código {codigo} já processado, pulando duplicata")
                    continue
                
                # Validar valores razoáveis (quantidade > 0, valores > 0)
                if quantidade <= 0 or valor_unitario <= 0 or valor_total <= 0:
                    print(f"DEBUG: Valores inválidos para produto {codigo}, pulando")
                    continue
                
                # Validar descrição não vazia e com tamanho razoável
                if not descricao or len(descricao.strip()) < 3:
                    print(f"DEBUG: Descrição inválida para produto {codigo}, pulando")
                    continue
                
                produto = {
                    'item': len(produtos) + 1,
                    'codigo': codigo,
                    'descricao': descricao,
                    'unidade': unidade,
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_total
                }
                codigos_processados.add(codigo)
                produtos.append(produto)
                print(f"DEBUG: Produto GIRASSOL extraído: {produto}")
                continue  # Próxima linha
        except Exception as e:
            print(f"DEBUG: Erro no parse GIRASSOL compacto: {e}")
        
        # 2) Padrões mais flexíveis para diferentes formatos de PDF
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
                        
                        # Validar se não é duplicata
                        if codigo in codigos_processados:
                            print(f"DEBUG: Código {codigo} já processado, pulando duplicata")
                            produto_encontrado = True  # Marcar como encontrado para não tentar outros padrões
                            break
                        
                        # Validar valores razoáveis (quantidade > 0, valores > 0)
                        if quantidade <= 0 or valor_unitario <= 0 or valor_total <= 0:
                            print(f"DEBUG: Valores inválidos para produto {codigo}, pulando")
                            continue
                        
                        # Validar descrição não vazia e com tamanho razoável
                        if not descricao or len(descricao.strip()) < 3:
                            print(f"DEBUG: Descrição inválida para produto {codigo}, pulando")
                            continue
                        
                        # Validar que a descrição não é apenas números (pode ser total/imposto)
                        if descricao.strip().replace('.', '').replace(',', '').isdigit():
                            print(f"DEBUG: Descrição parece ser número/total para {codigo}, pulando")
                            continue
                        
                        produto = {
                            'item': len(produtos) + 1,
                            'codigo': codigo,
                            'descricao': descricao,
                            'quantidade': quantidade,
                            'valor_unitario': valor_unitario,
                            'valor_total': valor_total
                        }
                        
                        codigos_processados.add(codigo)
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