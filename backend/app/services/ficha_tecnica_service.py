# backend/app/services/ficha_tecnica_service.py

import re
import os
from typing import Dict, Optional, List, Tuple
import pdfplumber
from PyPDF2 import PdfReader
from app.core.logger import app_logger

logger = app_logger


class FichaTecnicaService:
    """Serviço para extrair informações de fichas técnicas de PDFs"""
    
    def __init__(self):
        self.dilucao_patterns = [
            # Padrões comuns de diluição
            r'(\d+)\s*:\s*(\d+)',  # 1:10, 1:20, etc.
            r'(\d+)\s*/\s*(\d+)',  # 1/10, 1/20, etc.
            r'(\d+)\s+litro[s]?\s+para\s+(\d+)\s+litro[s]?',  # 1 litro para 10 litros
            r'(\d+)\s+parte[s]?\s+em\s+(\d+)\s+parte[s]?',  # 1 parte em 10 partes
            r'(\d+)\s+ml\s+para\s+(\d+)\s+litro[s]?',  # 100 ml para 10 litros
            r'(\d+)\s+ml\s+em\s+(\d+)\s+litro[s]?',  # 100 ml em 10 litros
            r'dilu[íi][çc][ãa]o[:\s]+(\d+)\s*[:\-/]\s*(\d+)',  # Diluição: 1:10
            r'dilu[íi][çc][ãa]o[:\s]+(\d+)\s+para\s+(\d+)',  # Diluição: 1 para 10
        ]
        
        self.rendimento_patterns = [
            r'rendimento[:\s]+(\d+[.,]?\d*)\s+litro[s]?',  # Rendimento: 10 litros
            r'(\d+[.,]?\d*)\s+litro[s]?\s+por\s+litro',  # 10 litros por litro
            r'(\d+[.,]?\d*)\s+litro[s]?\s+de\s+solu[çc][ãa]o',  # 10 litros de solução
            r'produz[:\s]+(\d+[.,]?\d*)\s+litro[s]?',  # Produz: 10 litros
        ]
    
    def extrair_texto_pdf(self, pdf_path: str) -> str:
        """Extrai texto de um arquivo PDF"""
        try:
            # Tentar primeiro com pdfplumber (melhor para tabelas)
            with pdfplumber.open(pdf_path) as pdf:
                texto_completo = ""
                for page in pdf.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
                return texto_completo
        except Exception as e:
            logger.warning(f"Erro ao extrair texto com pdfplumber: {e}. Tentando PyPDF2...")
            try:
                # Fallback para PyPDF2
                reader = PdfReader(pdf_path)
                texto_completo = ""
                for page in reader.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_completo += texto + "\n"
                return texto_completo
            except Exception as e2:
                logger.error(f"Erro ao extrair texto com PyPDF2: {e2}")
                raise
    
    def extrair_dilucao(self, texto: str) -> Optional[Tuple[float, float, str]]:
        """
        Extrai informações de diluição do texto.
        Retorna: (numerador, denominador, string_formatada) ou None
        """
        texto_lower = texto.lower()
        
        for pattern in self.dilucao_patterns:
            matches = re.finditer(pattern, texto_lower, re.IGNORECASE)
            for match in matches:
                try:
                    num = float(match.group(1))
                    den = float(match.group(2))
                    
                    # Normalizar: se o numerador for maior que o denominador, pode estar invertido
                    # Ex: "10 litros para 1 litro" = 1:10
                    if num > den and num > 10:
                        # Provavelmente está invertido (ex: 100 ml para 10 litros = 1:100)
                        if 'ml' in match.group(0) and 'litro' in match.group(0):
                            # Converter ml para litros
                            num_litros = num / 1000
                            if num_litros < den:
                                num, den = num_litros, den
                            else:
                                num, den = den, num_litros
                        else:
                            num, den = den, num
                    
                    # Formatar string
                    if num == 1:
                        dilucao_str = f"1:{int(den)}"
                    else:
                        dilucao_str = f"{int(num)}:{int(den)}"
                    
                    return (num, den, dilucao_str)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extrair_rendimento(self, texto: str) -> Optional[float]:
        """
        Extrai informação de rendimento do texto.
        Retorna: rendimento em litros por litro do produto ou None
        """
        texto_lower = texto.lower()
        
        for pattern in self.rendimento_patterns:
            matches = re.finditer(pattern, texto_lower, re.IGNORECASE)
            for match in matches:
                try:
                    valor_str = match.group(1).replace(',', '.')
                    rendimento = float(valor_str)
                    return rendimento
                except (ValueError, IndexError):
                    continue
        
        # Se não encontrou padrão específico, tentar calcular a partir da diluição
        dilucao = self.extrair_dilucao(texto)
        if dilucao:
            num, den, _ = dilucao
            # Rendimento = denominador / numerador
            # Ex: 1:10 = 10 litros por litro
            return den / num if num > 0 else None
        
        return None
    
    def extrair_modo_uso(self, texto: str) -> Optional[str]:
        """Extrai modo de uso do texto"""
        # Procurar por seções como "MODO DE USO", "APLICAÇÃO", "INSTRUÇÕES"
        secoes = [
            r'MODO\s+DE\s+USO[:\s]+(.+?)(?=\n\n|\n[A-Z]{3,}|$)',
            r'APLICA[ÇC][ÃA]O[:\s]+(.+?)(?=\n\n|\n[A-Z]{3,}|$)',
            r'INSTRU[ÇC][ÕO]ES[:\s]+(.+?)(?=\n\n|\n[A-Z]{3,}|$)',
            r'COMO\s+USAR[:\s]+(.+?)(?=\n\n|\n[A-Z]{3,}|$)',
        ]
        
        texto_upper = texto.upper()
        for pattern in secoes:
            match = re.search(pattern, texto, re.IGNORECASE | re.DOTALL)
            if match:
                modo_uso = match.group(1).strip()
                # Limpar o texto
                modo_uso = re.sub(r'\s+', ' ', modo_uso)
                if len(modo_uso) > 20:  # Só retornar se tiver conteúdo significativo
                    return modo_uso[:500]  # Limitar tamanho
        
        return None
    
    def extrair_dados_pdf(self, pdf_path: str) -> Dict:
        """
        Extrai todos os dados relevantes de um PDF de ficha técnica.
        Retorna dicionário com: nome_produto, dilucao, rendimento, modo_uso
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        # Extrair nome do produto do nome do arquivo
        nome_arquivo = os.path.basename(pdf_path)
        nome_produto = self._extrair_nome_produto_arquivo(nome_arquivo)
        
        # Extrair texto do PDF
        texto = self.extrair_texto_pdf(pdf_path)
        
        if not texto or len(texto.strip()) < 50:
            logger.warning(f"PDF {pdf_path} não contém texto suficiente")
            return {
                'nome_produto': nome_produto,
                'dilucao_recomendada': None,
                'dilucao_numerador': None,
                'dilucao_denominador': None,
                'rendimento_litro': None,
                'modo_uso': None,
                'arquivo_pdf_path': pdf_path
            }
        
        # Tentar extrair nome do produto do texto também
        nome_do_texto = self._extrair_nome_produto_texto(texto)
        if nome_do_texto and len(nome_do_texto) > len(nome_produto):
            nome_produto = nome_do_texto
        
        # Extrair informações
        dilucao = self.extrair_dilucao(texto)
        rendimento = self.extrair_rendimento(texto)
        modo_uso = self.extrair_modo_uso(texto)
        
        resultado = {
            'nome_produto': nome_produto,
            'arquivo_pdf_path': pdf_path,
            'modo_uso': modo_uso
        }
        
        if dilucao:
            num, den, dilucao_str = dilucao
            resultado.update({
                'dilucao_recomendada': dilucao_str,
                'dilucao_numerador': num,
                'dilucao_denominador': den
            })
        else:
            resultado.update({
                'dilucao_recomendada': None,
                'dilucao_numerador': None,
                'dilucao_denominador': None
            })
        
        resultado['rendimento_litro'] = rendimento
        
        return resultado
    
    def _extrair_nome_produto_arquivo(self, nome_arquivo: str) -> str:
        """Extrai nome do produto do nome do arquivo"""
        # Remover extensão
        nome = os.path.splitext(nome_arquivo)[0]
        # Remover palavras comuns
        palavras_remover = ['ficha', 'tecnica', 'ft', 'pdf', 'docx', '-', '_']
        for palavra in palavras_remover:
            nome = nome.replace(palavra, ' ')
        # Limpar espaços
        nome = ' '.join(nome.split())
        return nome.strip()
    
    def _extrair_nome_produto_texto(self, texto: str) -> Optional[str]:
        """Tenta extrair o nome do produto do texto do PDF"""
        # Procurar por padrões comuns no início do documento
        linhas = texto.split('\n')[:20]  # Primeiras 20 linhas
        
        for linha in linhas:
            linha = linha.strip()
            # Ignorar linhas muito curtas ou muito longas
            if len(linha) < 5 or len(linha) > 100:
                continue
            # Ignorar linhas que são claramente cabeçalhos
            if any(palavra in linha.upper() for palavra in ['FICHA', 'TECNICA', 'PAGINA', 'DATA']):
                continue
            # Se a linha parece um nome de produto (tem letras e números)
            if re.match(r'^[A-Z][A-Z0-9\s\-/]+$', linha.upper()):
                return linha.strip()
        
        return None
    
    def processar_pasta_pdfs(self, pasta: str) -> List[Dict]:
        """
        Processa todos os PDFs de uma pasta.
        Retorna lista de dicionários com dados extraídos.
        """
        resultados = []
        
        if not os.path.isdir(pasta):
            raise ValueError(f"Pasta não encontrada: {pasta}")
        
        arquivos_pdf = [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
        
        logger.info(f"Processando {len(arquivos_pdf)} arquivos PDF na pasta {pasta}")
        
        for arquivo in arquivos_pdf:
            caminho_completo = os.path.join(pasta, arquivo)
            try:
                dados = self.extrair_dados_pdf(caminho_completo)
                resultados.append(dados)
                logger.info(f"Processado: {arquivo} - Diluição: {dados.get('dilucao_recomendada')}, Rendimento: {dados.get('rendimento_litro')}")
            except Exception as e:
                logger.error(f"Erro ao processar {arquivo}: {e}")
                continue
        
        return resultados


# Instância global do serviço
ficha_tecnica_service = FichaTecnicaService()

