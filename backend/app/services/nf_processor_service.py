"""
Serviço principal de processamento de Notas Fiscais.
Integra extração de dados, identificação de empresa, reconhecimento de cliente,
relacionamento com vendedor e processamento de movimentações.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import re
import pdfplumber
import logging

from app.db import models
from app.services.empresa_service import EmpresaService
from app.services.cliente_matcher_service import ClienteMatcherService
from app.utils.cnpj_utils import extrair_cnpj_texto, normalizar_cnpj
from app.utils.product_matcher import find_product_by_code_or_name
from app.utils.pdf_extractor_melhorado import extrair_produtos_inteligente_entrada_melhorado

logger = logging.getLogger(__name__)


def _is_nome_cliente_invalido(nome: str) -> bool:
    """Rejeita nomes que são cabeçalhos de tabela (ex: 'Frete por Conta C') e não nomes reais de cliente."""
    if not nome or len(nome) < 3:
        return True
    nome_upper = nome.strip().upper()
    invalidos = (
        "FRETE POR CONTA",
        "FRETE POR CONTA C",
        "FRETE POR CONTA E",
        "9-SEM TRANSPORTE",
        "RAZAO SOCIAL",
        "NOME/RAZÃO SOCIAL",
    )
    return any(nome_upper == inv or nome_upper.startswith(inv + " ") for inv in invalidos)


class NFProcessorService:
    """Serviço principal para processamento de Notas Fiscais."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def processar_nf_pdf(
        self,
        caminho_pdf: str,
        tipo_movimentacao: str,
        vendedor_id: Optional[int] = None,
        orcamento_id: Optional[int] = None,
        usuario_id: int = None,
        empresa_id_override: Optional[int] = None,
        nome_arquivo_original: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa um PDF de NF completo: extrai dados, identifica empresa,
        reconhece/cria cliente, processa produtos e movimentações.
        
        Args:
            caminho_pdf: Caminho do arquivo PDF
            tipo_movimentacao: 'ENTRADA' ou 'SAIDA'
            vendedor_id: ID do vendedor responsável (opcional para NF de saída)
            orcamento_id: ID do orçamento relacionado (opcional)
            usuario_id: ID do usuário que está processando
            empresa_id_override: Forçar empresa_id (usado quando já identificado)
            
        Returns:
            Dicionário com resultado do processamento
        """
        try:
            # 1. Extrair texto do PDF
            import os
            # Usar nome original se fornecido, senão usar nome do arquivo temporário
            nome_arquivo_para_deteccao = (nome_arquivo_original or os.path.basename(caminho_pdf)).upper()
            logger.info(f"Processando PDF: nome_original={nome_arquivo_original}, caminho={caminho_pdf}, nome_para_deteccao={nome_arquivo_para_deteccao}")
            
            texto_completo = self._extrair_texto_pdf(caminho_pdf)
            logger.info(f"📄 Primeiros 1000 caracteres do texto extraído: {texto_completo[:1000] if texto_completo else 'VAZIO'}")
            
            # Se não conseguiu extrair texto, tentar detectar Delta Plástico pelo nome do arquivo
            texto_vazio = not texto_completo or not texto_completo.strip()
            if texto_vazio:
                logger.warning(f"Nenhum texto extraído do PDF. Verificando pelo nome do arquivo: nome_original='{nome_arquivo_original}', nome_deteccao='{nome_arquivo_para_deteccao}'")
                # Verificar se contém DELTA e PLAST/PLÁSTIC (case insensitive, tratando variações)
                tem_delta = "DELTA" in nome_arquivo_para_deteccao
                tem_plast = "PLAST" in nome_arquivo_para_deteccao or "PLÁSTIC" in nome_arquivo_para_deteccao.upper() or "PLASTICO" in nome_arquivo_para_deteccao
                
                if tem_delta and tem_plast:
                    logger.info(f"✓ PDF Delta Plástico detectado pelo nome do arquivo: {nome_arquivo_original or nome_arquivo_para_deteccao}")
                    # Criar texto mínimo para permitir processamento
                    texto_completo = f"DELTA PLASTICOS {nome_arquivo_original or nome_arquivo_para_deteccao}"
                else:
                    logger.error(f"✗ Não foi possível detectar Delta Plástico. nome_original='{nome_arquivo_original}', tem_delta={tem_delta}, tem_plast={tem_plast}")
                    raise ValueError(f"Não foi possível extrair texto do PDF '{nome_arquivo_original or nome_arquivo_para_deteccao}' e não foi possível identificar como Delta Plástico pelo nome do arquivo")
            
            # 2. Extrair dados básicos da NF
            dados_nf = self._extrair_dados_nf(texto_completo, tipo_movimentacao)
            
            # 3. Identificar empresa pelo CNPJ emitente
            empresa_id = self._identificar_empresa(
                texto_completo,
                dados_nf,
                empresa_id_override,
                nome_arquivo_original or caminho_pdf
            )
            
            if not empresa_id:
                raise ValueError("Não foi possível identificar a empresa da NF")
            
            # 4. Detectar se é Delta Plástico (entrada especial)
            is_delta_plastico = self._detectar_delta_plastico(texto_completo, dados_nf, nome_arquivo_original or caminho_pdf)
            if is_delta_plastico:
                tipo_movimentacao = "ENTRADA"
                # Se for Delta Plástico, garantir que o fornecedor está definido
                if not dados_nf.get('fornecedor'):
                    dados_nf['fornecedor'] = "Delta Plásticos"
            
            # 5. Para NF de saída, reconhecer/criar cliente
            cliente_id = None
            if tipo_movimentacao == "SAIDA":
                cliente = self._reconhecer_ou_criar_cliente(
                    texto_completo,
                    dados_nf,
                    empresa_id
                )
                cliente_id = cliente.id if cliente else None
                
                # Se vendedor não fornecido mas há orçamento, buscar do orçamento
                if not vendedor_id and orcamento_id:
                    vendedor_id = self._obter_vendedor_do_orcamento(orcamento_id)
                
                # Se ainda não tem vendedor, tentar buscar do cliente
                if not vendedor_id and cliente:
                    vendedor_id = cliente.vendedor_id
            
            # 6. Extrair produtos
            if tipo_movimentacao == "ENTRADA":
                produtos = extrair_produtos_inteligente_entrada_melhorado(texto_completo)
            else:
                produtos = self._extrair_produtos_saida(texto_completo)
            
            # 7. Processar produtos e criar preview
            preview = self._criar_preview_produtos(
                produtos,
                empresa_id,
                tipo_movimentacao
            )
            
            return {
                'sucesso': True,
                'tipo_movimentacao': tipo_movimentacao,
                'empresa_id': empresa_id,
                'nota_fiscal': dados_nf.get('nota_fiscal'),
                'data_emissao': dados_nf.get('data_emissao'),
                'cliente_id': cliente_id,
                'cliente': dados_nf.get('cliente'),
                'cnpj_cliente': dados_nf.get('cnpj_cliente'),
                'vendedor_id': vendedor_id,
                'orcamento_id': orcamento_id,
                'is_delta_plastico': is_delta_plastico,
                'valor_total': dados_nf.get('valor_total'),
                'produtos': preview['produtos'],
                'produtos_encontrados': preview['encontrados'],
                'produtos_nao_encontrados': preview['nao_encontrados'],
                'total_produtos': len(produtos)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar NF: {str(e)}", exc_info=True)
            raise
    
    def confirmar_processamento(
        self,
        dados_confirmacao: Dict[str, Any],
        usuario_id: int
    ) -> Dict[str, Any]:
        """
        Confirma e processa as movimentações após revisão pelo usuário.
        
        Args:
            dados_confirmacao: Dados confirmados pelo usuário:
                - nota_fiscal: Número da NF
                - tipo_movimentacao: ENTRADA ou SAIDA
                - empresa_id: ID da empresa
                - cliente_id: ID do cliente (para saída)
                - vendedor_id: ID do vendedor (para saída)
                - orcamento_id: ID do orçamento (opcional)
                - produtos_confirmados: Lista de produtos a processar
            usuario_id: ID do usuário confirmando
            
        Returns:
            Dicionário com resultado do processamento
        """
        from app.services.stock_service import StockService
        from app.crud import movimentacao_estoque as crud_movimentacao
        from app.schemas import movimentacao_estoque as schemas_movimentacao
        
        produtos_confirmados = dados_confirmacao.get('produtos_confirmados', [])
        tipo_movimentacao = dados_confirmacao.get('tipo_movimentacao')
        empresa_id = dados_confirmacao.get('empresa_id')
        cliente_id = dados_confirmacao.get('cliente_id')
        vendedor_id = dados_confirmacao.get('vendedor_id')
        orcamento_id = dados_confirmacao.get('orcamento_id')
        nota_fiscal = dados_confirmacao.get('nota_fiscal')
        
        if not produtos_confirmados:
            raise ValueError("Nenhum produto foi confirmado para processamento")
        
        movimentacoes_criadas = []
        historicos_vendas = []
        
        for produto_data in produtos_confirmados:
            produto_id = produto_data.get('produto_id')
            quantidade = produto_data.get('quantidade', 0)
            valor_unitario = produto_data.get('valor_unitario', 0)
            valor_total = produto_data.get('valor_total', 0)
            
            if not produto_id or quantidade <= 0:
                continue
            
            # Criar movimentação
            observacao = f"NF {nota_fiscal} - Processamento automático"
            if tipo_movimentacao == "SAIDA" and cliente_id:
                cliente = self.db.query(models.Cliente).filter(
                    models.Cliente.id == cliente_id
                ).first()
                if cliente:
                    observacao += f" - Cliente: {cliente.razao_social}"
            
            movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
                produto_id=produto_id,
                tipo_movimentacao=tipo_movimentacao,
                quantidade=quantidade,
                observacao=observacao
            )
            
            produto_atualizado = crud_movimentacao.create_movimentacao_estoque(
                db=self.db,
                movimentacao=movimentacao_data,
                usuario_id=usuario_id,
                empresa_id=empresa_id
            )
            
            movimentacoes_criadas.append({
                'produto_id': produto_id,
                'quantidade': quantidade,
                'estoque_atual': produto_atualizado.quantidade_em_estoque
            })
            
            # Para saída, criar histórico de venda e preço (SEMPRE quando houver cliente)
            if tipo_movimentacao == "SAIDA":
                # Se não temos cliente_id mas temos CNPJ nos dados, buscar/criar cliente
                cnpj_cliente = dados_confirmacao.get('cnpj_cliente')
                if not cliente_id and cnpj_cliente:
                    try:
                        cliente = ClienteMatcherService.encontrar_ou_criar_cliente(
                            db=self.db,
                            cnpj=cnpj_cliente,
                            razao_social=dados_confirmacao.get('cliente'),
                            empresa_id=empresa_id
                        )
                        cliente_id = cliente.id if cliente else None
                        logger.info(f"Cliente identificado/criado pelo CNPJ {cnpj_cliente}: ID {cliente_id}")
                    except Exception as e:
                        logger.warning(f"Erro ao buscar/criar cliente pelo CNPJ {cnpj_cliente}: {e}")
                
                # Criar HistoricoPrecoProduto SEMPRE que houver SAÍDA com cliente e valor
                # Este é o registro principal que vincula NF-e verificada ao cliente (via CNPJ)
                if cliente_id and valor_unitario > 0 and nota_fiscal:
                    historico_preco = models.HistoricoPrecoProduto(
                        produto_id=produto_id,
                        preco_unitario=valor_unitario,
                        quantidade=quantidade,
                        valor_total=valor_total,
                        nota_fiscal=nota_fiscal,  # Obrigatório - dados verificados via NF-e
                        empresa_id=empresa_id,
                        cliente_id=cliente_id  # Vinculado via CNPJ
                    )
                    self.db.add(historico_preco)
                    logger.info(f"Histórico de preço criado: Cliente {cliente_id}, Produto {produto_id}, NF {nota_fiscal}")
                    
                    # Criar HistoricoVendaCliente apenas se houver orcamento_id
                    # (pois o modelo exige orcamento_id como obrigatório)
                    if orcamento_id:
                        vendedor_para_historico = vendedor_id or usuario_id
                        historico_venda = models.HistoricoVendaCliente(
                            vendedor_id=vendedor_para_historico,
                            cliente_id=cliente_id,
                            produto_id=produto_id,
                            orcamento_id=orcamento_id,
                            empresa_id=empresa_id,
                            quantidade_vendida=int(quantidade),
                            preco_unitario_vendido=valor_unitario,
                            valor_total=valor_total,
                            data_venda=datetime.now()
                        )
                        self.db.add(historico_venda)
                        historicos_vendas.append(historico_venda.id)
                        logger.info(f"Histórico de venda criado para cliente {cliente_id}, produto {produto_id}, NF {nota_fiscal}")
        
        # Vincular orçamento à NF se fornecido
        if orcamento_id and tipo_movimentacao == "SAIDA":
            orcamento = self.db.query(models.Orcamento).filter(
                models.Orcamento.id == orcamento_id
            ).first()
            if orcamento:
                orcamento.numero_nf = nota_fiscal
                # Se status ainda é RASCUNHO ou ENVIADO, pode marcar como relacionado
                logger.info(f"NF {nota_fiscal} vinculada ao orçamento {orcamento_id}")
        
        self.db.commit()
        
        return {
            'sucesso': True,
            'movimentacoes_criadas': len(movimentacoes_criadas),
            'historicos_vendas': len(historicos_vendas),
            'detalhes': movimentacoes_criadas
        }
    
    def _extrair_texto_pdf(self, caminho_pdf: str) -> str:
        """Extrai texto completo de um PDF usando múltiplas bibliotecas como fallback."""
        texto = ""
        
        # Tentar primeiro com pdfplumber (melhor para tabelas e texto estruturado)
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        texto += page_text + "\n"
            if texto.strip():
                logger.info(f"Texto extraído com pdfplumber: {len(texto)} caracteres")
                return texto
        except Exception as e:
            logger.warning(f"Erro ao extrair texto com pdfplumber: {e}. Tentando PyPDF2...")
        
        # Fallback para PyPDF2/pypdf se pdfplumber falhar ou não retornar texto
        try:
            # Tentar importar PyPDF2 (versões antigas) ou pypdf (versões novas)
            try:
                from pypdf import PdfReader
            except ImportError:
                try:
                    import PyPDF2
                    PdfReader = PyPDF2.PdfReader
                except ImportError:
                    raise ImportError("Nem pypdf nem PyPDF2 estão disponíveis")
            
            reader = PdfReader(caminho_pdf)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    texto += page_text + "\n"
            if texto.strip():
                logger.info(f"Texto extraído com PyPDF2/pypdf: {len(texto)} caracteres")
                return texto
        except ImportError as imp_err:
            logger.warning(f"PyPDF2/pypdf não disponível: {imp_err}. Pulando fallback.")
        except Exception as e2:
            logger.warning(f"Erro ao extrair texto com PyPDF2/pypdf: {e2}")
        
        # Se nenhuma biblioteca conseguiu extrair texto, retornar string vazia
        # (permitir processamento baseado em nome do arquivo ou outras heurísticas)
        if not texto.strip():
            logger.warning(f"Não foi possível extrair texto do PDF {caminho_pdf}. Retornando string vazia para permitir detecção por nome do arquivo.")
        
        return texto
    
    def _extrair_dados_nf(
        self,
        texto_completo: str,
        tipo_movimentacao: str
    ) -> Dict[str, Any]:
        """Extrai dados básicos da NF (número, data, cliente/fornecedor, etc)."""
        dados = {
            'nota_fiscal': None,
            'data_emissao': None,
            'cliente': None,
            'cnpj_cliente': None,
            'fornecedor': None,
            'cnpj_fornecedor': None,
            'valor_total': None
        }
        
        # Extrair número da NF
        nf_patterns = [
            r'NFe\s+Nº\s+(\d+)',
            r'NOTA FISCAL ELETRÔNICA[\s\S]*?Nº\s*(\d+)',
            r'N[úu]mero[:\s]+(\d+)',
            r'NF[\s-]*e?[:\s]*(\d+)',
        ]
        
        for pattern in nf_patterns:
            match = re.search(pattern, texto_completo, re.IGNORECASE)
            if match:
                dados['nota_fiscal'] = match.group(1)
                break
        
        # Extrair data de emissão
        data_patterns = [
            r'Data de Emissão\s+(\d{2}/\d{2}/\d{4})',
            r'DATA DE EMISSÃO[:\s]+(\d{2}/\d{2}/\d{4})',
            r'Emissão[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        ]
        
        for pattern in data_patterns:
            match = re.search(pattern, texto_completo, re.IGNORECASE)
            if match:
                dados['data_emissao'] = match.group(1)
                break
        
        # Extrair CNPJs
        cnpjs = extrair_cnpj_texto(texto_completo)
        
        if tipo_movimentacao == "SAIDA":
            # Para saída, cliente é o destinatário
            # Geralmente o segundo CNPJ é do destinatário
            if len(cnpjs) >= 2:
                dados['cnpj_cliente'] = cnpjs[1]
            elif len(cnpjs) == 1:
                dados['cnpj_cliente'] = cnpjs[0]
            
            # Extrair nome do cliente
            cliente_patterns = [
                r'Nome/Razão Social\s+([A-Z][A-Z\s&.-]+?)\s+\d{2}\.\d{3}\.\d{3}',
                r'Destinatário[:\s]+([A-Z][A-Z\s&.-]+?)(?=\s+CNPJ)',
            ]
            
            for pattern in cliente_patterns:
                match = re.search(pattern, texto_completo, re.IGNORECASE)
                if match:
                    nome_extraido = match.group(1).strip()
                    # Ignorar nomes inválidos - "Frete por Conta C/E" é cabeçalho da tabela de transporte, não nome de cliente
                    if nome_extraido and not _is_nome_cliente_invalido(nome_extraido):
                        dados['cliente'] = nome_extraido
                    break
        else:
            # Para entrada, fornecedor é o remetente
            # Geralmente o primeiro CNPJ é do remetente
            if cnpjs:
                dados['cnpj_fornecedor'] = cnpjs[0]
            
            # Extrair nome do fornecedor
            fornecedor_patterns = [
                r'Remetente[:\s]+([A-Z][A-Z\s&.-]+?)\s+\d{2}\.\d{3}\.\d{3}',
                r'RAZÃO SOCIAL[\s\n]+([A-Z][A-Z\s&.-]+?)(?=\s+CNPJ)',
            ]
            
            for pattern in fornecedor_patterns:
                match = re.search(pattern, texto_completo, re.IGNORECASE)
                if match:
                    dados['fornecedor'] = match.group(1).strip()
                    break
        
        # Extrair valor total
        valor_patterns = [
            r'Valor Total da Nota\s+Fiscal\s+([\d.,]+)',
            r'VALOR TOTAL DA NOTA[\s\n]+([\d.,]+)',
            r'Total\s+Geral[:\s]+R?\$?\s*([\d.,]+)',
        ]
        
        for pattern in valor_patterns:
            match = re.search(pattern, texto_completo, re.IGNORECASE)
            if match:
                valor_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    dados['valor_total'] = float(valor_str)
                except ValueError:
                    pass
                break
        
        return dados
    
    def _identificar_empresa(
        self,
        texto_completo: str,
        dados_nf: Dict[str, Any],
        empresa_id_override: Optional[int],
        caminho_pdf: Optional[str] = None
    ) -> Optional[int]:
        """Identifica empresa pelo CNPJ emitente ou contexto."""
        if empresa_id_override:
            logger.info(f"Empresa ID override fornecido: {empresa_id_override}")
            return empresa_id_override
        
        # Extrair CNPJ do emitente (primeiro CNPJ geralmente)
        cnpjs = extrair_cnpj_texto(texto_completo)
        logger.info(f"CNPJs encontrados no texto: {cnpjs}")
        
        # Buscar por CNPJ da HIGIPLAS ou HIGITEC no texto
        # Se encontrar um dos CNPJs conhecidos, identificar empresa
        for cnpj in cnpjs:
            empresa_id = EmpresaService.identificar_empresa_por_cnpj(self.db, cnpj)
            if empresa_id:
                logger.info(f"Empresa identificada pelo CNPJ {cnpj}: ID {empresa_id}")
                return empresa_id
        
        # Se não encontrou pelos CNPJs, tentar pelo contexto do texto
        texto_upper = texto_completo.upper() if texto_completo else ''
        logger.info(f"Tentando identificar empresa por palavras-chave no texto (primeiros 500 chars): {texto_upper[:500]}")
        
        if "HIGIPLAS" in texto_upper:
            empresa_id = EmpresaService.get_empresa_id(self.db, "HIGIPLAS")
            if empresa_id:
                logger.info(f"Empresa identificada como HIGIPLAS por palavra-chave: ID {empresa_id}")
                return empresa_id
        
        if "HIGITEC" in texto_upper:
            empresa_id = EmpresaService.get_empresa_id(self.db, "HIGITEC")
            if empresa_id:
                logger.info(f"Empresa identificada como HIGITEC por palavra-chave: ID {empresa_id}")
                return empresa_id
        
        # Se ainda não encontrou e é Delta Plástico, usar HIGIPLAS como padrão
        # (Delta Plástico é fornecedor de HIGIPLAS)
        if caminho_pdf:
            import os
            nome_arquivo = os.path.basename(caminho_pdf).upper()
            if "DELTA" in nome_arquivo and "PLAST" in nome_arquivo:
                empresa_id = EmpresaService.get_empresa_id(self.db, "HIGIPLAS")
                if empresa_id:
                    logger.info("Empresa identificada como HIGIPLAS baseado no nome do arquivo Delta Plástico")
                    return empresa_id
        
        logger.error(f"❌ Não foi possível identificar a empresa. CNPJs encontrados: {cnpjs}, Nome do arquivo: {caminho_pdf}")
        return None
    
    def _detectar_delta_plastico(
        self,
        texto_completo: str,
        dados_nf: Dict[str, Any],
        caminho_pdf: Optional[str] = None
    ) -> bool:
        """Detecta se é NF do Delta Plástico (sacos de lixo - entrada especial)."""
        # Detectar pelo nome do fornecedor (tratando caso None)
        fornecedor = dados_nf.get('fornecedor') or ''
        fornecedor = str(fornecedor).upper() if fornecedor else ''
        texto_upper = texto_completo.upper() if texto_completo else ''
        
        # Verificar no fornecedor
        if fornecedor and "DELTA" in fornecedor and "PLASTIC" in fornecedor:
            return True
        
        # Verificar no texto extraído
        if "DELTA PLAST" in texto_upper:
            return True
        
        # Verificar pelo nome do arquivo como fallback
        if caminho_pdf:
            import os
            nome_arquivo = os.path.basename(caminho_pdf).upper()
            if "DELTA" in nome_arquivo and "PLAST" in nome_arquivo:
                return True
        
        return False
    
    def _reconhecer_ou_criar_cliente(
        self,
        texto_completo: str,
        dados_nf: Dict[str, Any],
        empresa_id: int
    ) -> Optional[models.Cliente]:
        """Reconhece ou cria cliente automaticamente."""
        cnpj = dados_nf.get('cnpj_cliente')
        if not cnpj:
            return None
        
        try:
            dados_cliente = ClienteMatcherService.extrair_dados_cliente_da_nf(
                texto_completo,
                empresa_id
            )
            
            cliente = ClienteMatcherService.encontrar_ou_criar_cliente(
                db=self.db,
                cnpj=cnpj,
                razao_social=dados_cliente.get('razao_social') or dados_nf.get('cliente'),
                endereco=dados_cliente.get('endereco'),
                telefone=dados_cliente.get('telefone'),
                email=dados_cliente.get('email'),
                empresa_id=empresa_id
            )
            
            return cliente
        except Exception as e:
            logger.warning(f"Erro ao reconhecer/criar cliente: {e}")
            return None
    
    def _obter_vendedor_do_orcamento(self, orcamento_id: int) -> Optional[int]:
        """Obtém vendedor vinculado ao orçamento."""
        orcamento = self.db.query(models.Orcamento).filter(
            models.Orcamento.id == orcamento_id
        ).first()
        
        if orcamento and orcamento.usuario_id:
            return orcamento.usuario_id
        
        return None
    
    def _extrair_produtos_saida(self, texto_completo: str) -> List[Dict[str, Any]]:
        """Extrai produtos de uma NF de saída."""
        produtos = []
        linhas = texto_completo.split('\n')
        
        # Buscar seção de produtos
        inicio_produtos = False
        for linha in linhas:
            if 'Dados dos Produtos' in linha or 'DADOS DOS PRODUTOS' in linha:
                inicio_produtos = True
                continue
            
            if inicio_produtos and ('Dados Adicionais' in linha or 'DADOS ADICIONAIS' in linha):
                break
            
            if inicio_produtos:
                # Padrão: ITEM CÓDIGO DESCRIÇÃO NCM CST CFOP UN QTD VALOR_UNIT VALOR_TOTAL
                match = re.match(
                    r'^(\d+)\s+(\d+)\s+(.+?)\s+(\d{8})\s+\d{4}\s+\d{4}\s+(\w+)\s+([\d,]+)\s+([\d,]+)\s+[\d,]*\s*([\d,]+)',
                    linha.strip()
                )
                
                if match:
                    try:
                        produtos.append({
                            'item': int(match.group(1)),
                            'codigo': match.group(2),
                            'descricao': match.group(3).strip(),
                            'ncm': match.group(4),
                            'unidade': match.group(5),
                            'quantidade': float(match.group(6).replace(',', '.')),
                            'valor_unitario': float(match.group(7).replace(',', '.')),
                            'valor_total': float(match.group(8).replace(',', '.'))
                        })
                    except (ValueError, IndexError):
                        continue
        
        return produtos
    
    def _criar_preview_produtos(
        self,
        produtos: List[Dict[str, Any]],
        empresa_id: int,
        tipo_movimentacao: str
    ) -> Dict[str, Any]:
        """Cria preview dos produtos com associações ao banco."""
        produtos_encontrados = []
        produtos_nao_encontrados = []
        
        for produto_data in produtos:
            codigo = produto_data.get('codigo')
            descricao = produto_data.get('descricao', '')
            quantidade = produto_data.get('quantidade', 0)
            valor_unitario = produto_data.get('valor_unitario', 0)
            valor_total = produto_data.get('valor_total', 0)
            
            # Buscar produto no banco
            produto_encontrado, metodo, score = find_product_by_code_or_name(
                self.db,
                codigo or '',
                descricao,
                empresa_id,
                threshold=0.5
            )
            
            produto_info = {
                'codigo': codigo,
                'descricao': descricao,
                'quantidade': quantidade,
                'valor_unitario': valor_unitario,
                'valor_total': valor_total,
                'encontrado': produto_encontrado is not None,
                'metodo_busca': metodo,
                'score_similaridade': score
            }
            
            if produto_encontrado:
                produto_info.update({
                    'produto_id': produto_encontrado.id,
                    'nome_sistema': produto_encontrado.nome,
                    'estoque_atual': produto_encontrado.quantidade_em_estoque,
                    'estoque_projetado': (
                        produto_encontrado.quantidade_em_estoque + quantidade
                        if tipo_movimentacao == "ENTRADA"
                        else produto_encontrado.quantidade_em_estoque - quantidade
                    )
                })
                produtos_encontrados.append(produto_info)
            else:
                produtos_nao_encontrados.append(produto_info)
        
        return {
            'produtos': produtos_encontrados + produtos_nao_encontrados,
            'encontrados': produtos_encontrados,
            'nao_encontrados': produtos_nao_encontrados
        }
