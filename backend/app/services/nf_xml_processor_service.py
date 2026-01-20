"""
Serviço para processamento de XML de Notas Fiscais Eletrônicas (NF-e) brasileiras.
Extrai dados estruturados do XML seguindo padrão SEFAZ.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import xml.etree.ElementTree as ET
from lxml import etree
import logging
import re

from app.db import models
from app.services.empresa_service import EmpresaService
from app.services.cliente_matcher_service import ClienteMatcherService
from app.utils.cnpj_utils import normalizar_cnpj
from app.utils.product_matcher import find_product_by_code_or_name

logger = logging.getLogger(__name__)


class NFXMLProcessorService:
    """Serviço para processamento de XML de NF-e brasileira."""
    
    # Namespaces comuns da NF-e (podem variar por versão)
    NAMESPACES = {
        'nfe': 'http://www.portalfiscal.inf.br/nfe',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def processar_nf_xml(
        self,
        caminho_xml: str,
        tipo_movimentacao: str = None,
        empresa_id_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processa XML de NF-e e extrai todos os dados estruturados.
        
        Args:
            caminho_xml: Caminho do arquivo XML
            tipo_movimentacao: 'ENTRADA' ou 'SAIDA' (pode ser None para auto-detectar)
            empresa_id_override: Forçar empresa_id (opcional)
            
        Returns:
            Dicionário com dados extraídos da NF-e
        """
        try:
            # Parse do XML
            tree = ET.parse(caminho_xml)
            root = tree.getroot()
            
            # Detectar namespace dinamicamente
            ns = self._detectar_namespace(root)
            
            # Extrair dados básicos
            dados_nf = self._extrair_dados_basicos(root, ns)
            
            # Auto-detectar tipo de movimentação se não fornecido
            if not tipo_movimentacao:
                tipo_movimentacao = self._detectar_tipo_movimentacao(root, ns, empresa_id_override)
            
            # Identificar empresa
            empresa_id = self._identificar_empresa(root, ns, empresa_id_override)
            if not empresa_id:
                raise ValueError("Não foi possível identificar a empresa da NF-e")
            
            # Extrair emitente e destinatário
            emitente = self._extrair_emitente(root, ns)
            destinatario = self._extrair_destinatario(root, ns)
            
            # Extrair produtos
            produtos = self._extrair_produtos(root, ns)
            
            # Extrair totais
            totais = self._extrair_totais(root, ns)
            
            # Determinar cliente/fornecedor baseado no tipo
            cliente_id = None
            cnpj_cliente = None
            nome_cliente = None
            
            if tipo_movimentacao == "SAIDA":
                cnpj_cliente = destinatario.get('cnpj')
                nome_cliente = destinatario.get('nome')
                
                # Buscar ou criar cliente pelo CNPJ
                if cnpj_cliente:
                    try:
                        cliente = ClienteMatcherService.encontrar_ou_criar_cliente(
                            db=self.db,
                            cnpj=cnpj_cliente,
                            razao_social=nome_cliente,
                            endereco=destinatario.get('endereco'),
                            telefone=destinatario.get('telefone'),
                            email=destinatario.get('email'),
                            empresa_id=empresa_id
                        )
                        cliente_id = cliente.id if cliente else None
                        logger.info(f"Cliente identificado/criado pelo CNPJ {cnpj_cliente}: ID {cliente_id}")
                    except Exception as e:
                        logger.warning(f"Erro ao buscar/criar cliente pelo CNPJ {cnpj_cliente}: {e}")
            
            # Criar preview de produtos com associações ao banco
            preview = self._criar_preview_produtos(produtos, empresa_id, tipo_movimentacao)
            
            return {
                'sucesso': True,
                'tipo_movimentacao': tipo_movimentacao,
                'empresa_id': empresa_id,
                'nota_fiscal': dados_nf.get('numero'),
                'chave_acesso': dados_nf.get('chave_acesso'),
                'data_emissao': dados_nf.get('data_emissao'),
                'cliente_id': cliente_id,
                'cliente': nome_cliente,
                'cnpj_cliente': cnpj_cliente,
                'cnpj_emitente': emitente.get('cnpj'),
                'nome_emitente': emitente.get('nome'),
                'valor_total': totais.get('valor_total'),
                'produtos': preview['produtos'],
                'produtos_encontrados': preview['encontrados'],
                'produtos_nao_encontrados': preview['nao_encontrados'],
                'total_produtos': len(produtos)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar XML de NF-e: {str(e)}", exc_info=True)
            raise
    
    def _detectar_namespace(self, root: ET.Element) -> Dict[str, str]:
        """Detecta namespace do XML dinamicamente."""
        # Tentar namespaces comuns
        for prefix, uri in self.NAMESPACES.items():
            try:
                # Testar se existe elemento com este namespace
                test_elem = root.find(f'.//{{{uri}}}infNFe')
                if test_elem is not None:
                    return {prefix: uri}
            except:
                continue
        
        # Se não encontrou, usar namespace padrão
        return {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    
    def _extrair_dados_basicos(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados básicos da NF-e (número, data, chave de acesso)."""
        dados = {
            'numero': None,
            'serie': None,
            'data_emissao': None,
            'chave_acesso': None
        }
        
        # Buscar infNFe
        inf_nfe = root.find('.//{http://www.portalfiscal.inf.br/nfe}infNFe')
        if inf_nfe is None:
            # Tentar sem namespace
            inf_nfe = root.find('.//infNFe')
        
        if inf_nfe is not None:
            # Chave de acesso (atributo Id)
            chave_acesso = inf_nfe.get('Id', '')
            if chave_acesso:
                dados['chave_acesso'] = chave_acesso.replace('NFe', '')
            
            # Buscar ide (identificação)
            ide = inf_nfe.find('.//{http://www.portalfiscal.inf.br/nfe}ide')
            if ide is None:
                ide = inf_nfe.find('.//ide')
            
            if ide is not None:
                n_num = ide.find('.//{http://www.portalfiscal.inf.br/nfe}nNF')
                if n_num is None:
                    n_num = ide.find('.//nNF')
                if n_num is not None:
                    dados['numero'] = n_num.text
                
                serie = ide.find('.//{http://www.portalfiscal.inf.br/nfe}serie')
                if serie is None:
                    serie = ide.find('.//serie')
                if serie is not None:
                    dados['serie'] = serie.text
                
                dh_emi = ide.find('.//{http://www.portalfiscal.inf.br/nfe}dhEmi')
                if dh_emi is None:
                    dh_emi = ide.find('.//dhEmi')
                if dh_emi is not None:
                    # Converter formato ISO para datetime
                    try:
                        data_str = dh_emi.text
                        # Formato: 2025-01-15T10:30:00-03:00
                        data_str = data_str.split('-03:00')[0].split('-04:00')[0]  # Remover timezone
                        dados['data_emissao'] = datetime.fromisoformat(data_str).strftime('%d/%m/%Y')
                    except:
                        dados['data_emissao'] = dh_emi.text
        
        return dados
    
    def _extrair_emitente(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados do emitente."""
        emitente = {
            'cnpj': None,
            'nome': None,
            'endereco': None,
            'telefone': None,
            'email': None
        }
        
        emit = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
        if emit is None:
            emit = root.find('.//emit')
        
        if emit is not None:
            cnpj = emit.find('.//{http://www.portalfiscal.inf.br/nfe}CNPJ')
            if cnpj is None:
                cnpj = emit.find('.//CNPJ')
            if cnpj is not None:
                emitente['cnpj'] = cnpj.text
            
            nome = emit.find('.//{http://www.portalfiscal.inf.br/nfe}xNome')
            if nome is None:
                nome = emit.find('.//xNome')
            if nome is not None:
                emitente['nome'] = nome.text
            
            # Endereço
            ender_emit = emit.find('.//{http://www.portalfiscal.inf.br/nfe}enderEmit')
            if ender_emit is None:
                ender_emit = emit.find('.//enderEmit')
            
            if ender_emit is not None:
                x_lgr = ender_emit.find('.//{http://www.portalfiscal.inf.br/nfe}xLgr')
                if x_lgr is None:
                    x_lgr = ender_emit.find('.//xLgr')
                nro = ender_emit.find('.//{http://www.portalfiscal.inf.br/nfe}nro')
                if nro is None:
                    nro = ender_emit.find('.//nro')
                bairro = ender_emit.find('.//{http://www.portalfiscal.inf.br/nfe}xBairro')
                if bairro is None:
                    bairro = ender_emit.find('.//xBairro')
                cidade = ender_emit.find('.//{http://www.portalfiscal.inf.br/nfe}xMun')
                if cidade is None:
                    cidade = ender_emit.find('.//xMun')
                
                endereco_parts = []
                if x_lgr is not None:
                    endereco_parts.append(x_lgr.text)
                if nro is not None:
                    endereco_parts.append(nro.text)
                if bairro is not None:
                    endereco_parts.append(bairro.text)
                if cidade is not None:
                    endereco_parts.append(cidade.text)
                
                emitente['endereco'] = ', '.join(endereco_parts) if endereco_parts else None
        
        return emitente
    
    def _extrair_destinatario(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados do destinatário."""
        destinatario = {
            'cnpj': None,
            'nome': None,
            'endereco': None,
            'telefone': None,
            'email': None
        }
        
        dest = root.find('.//{http://www.portalfiscal.inf.br/nfe}dest')
        if dest is None:
            dest = root.find('.//dest')
        
        if dest is not None:
            cnpj = dest.find('.//{http://www.portalfiscal.inf.br/nfe}CNPJ')
            if cnpj is None:
                cnpj = dest.find('.//CNPJ')
            if cnpj is not None:
                destinatario['cnpj'] = cnpj.text
            
            nome = dest.find('.//{http://www.portalfiscal.inf.br/nfe}xNome')
            if nome is None:
                nome = dest.find('.//xNome')
            if nome is not None:
                destinatario['nome'] = nome.text
            
            # Endereço
            ender_dest = dest.find('.//{http://www.portalfiscal.inf.br/nfe}enderDest')
            if ender_dest is None:
                ender_dest = dest.find('.//enderDest')
            
            if ender_dest is not None:
                x_lgr = ender_dest.find('.//{http://www.portalfiscal.inf.br/nfe}xLgr')
                if x_lgr is None:
                    x_lgr = ender_dest.find('.//xLgr')
                nro = ender_dest.find('.//{http://www.portalfiscal.inf.br/nfe}nro')
                if nro is None:
                    nro = ender_dest.find('.//nro')
                bairro = ender_dest.find('.//{http://www.portalfiscal.inf.br/nfe}xBairro')
                if bairro is None:
                    bairro = ender_dest.find('.//xBairro')
                cidade = ender_dest.find('.//{http://www.portalfiscal.inf.br/nfe}xMun')
                if cidade is None:
                    cidade = ender_dest.find('.//xMun')
                
                endereco_parts = []
                if x_lgr is not None:
                    endereco_parts.append(x_lgr.text)
                if nro is not None:
                    endereco_parts.append(nro.text)
                if bairro is not None:
                    endereco_parts.append(bairro.text)
                if cidade is not None:
                    endereco_parts.append(cidade.text)
                
                destinatario['endereco'] = ', '.join(endereco_parts) if endereco_parts else None
            
            # Telefone
            fone = dest.find('.//{http://www.portalfiscal.inf.br/nfe}fone')
            if fone is None:
                fone = dest.find('.//fone')
            if fone is not None:
                destinatario['telefone'] = fone.text
            
            # Email
            email = dest.find('.//{http://www.portalfiscal.inf.br/nfe}email')
            if email is None:
                email = dest.find('.//email')
            if email is not None:
                destinatario['email'] = email.text
        
        return destinatario
    
    def _extrair_produtos(self, root: ET.Element, ns: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extrai lista de produtos da NF-e."""
        produtos = []
        
        # Buscar todos os elementos det (detalhes/produtos)
        dets = root.findall('.//{http://www.portalfiscal.inf.br/nfe}det')
        if not dets:
            dets = root.findall('.//det')
        
        for det in dets:
            produto = {}
            
            # Buscar prod (produto)
            prod = det.find('.//{http://www.portalfiscal.inf.br/nfe}prod')
            if prod is None:
                prod = det.find('.//prod')
            
            if prod is not None:
                # Código do produto
                c_prod = prod.find('.//{http://www.portalfiscal.inf.br/nfe}cProd')
                if c_prod is None:
                    c_prod = prod.find('.//cProd')
                if c_prod is not None:
                    produto['codigo'] = c_prod.text
                
                # Descrição
                x_prod = prod.find('.//{http://www.portalfiscal.inf.br/nfe}xProd')
                if x_prod is None:
                    x_prod = prod.find('.//xProd')
                if x_prod is not None:
                    produto['descricao'] = x_prod.text
                
                # NCM
                ncm = prod.find('.//{http://www.portalfiscal.inf.br/nfe}NCM')
                if ncm is None:
                    ncm = prod.find('.//NCM')
                if ncm is not None:
                    produto['ncm'] = ncm.text
                
                # Unidade
                u_com = prod.find('.//{http://www.portalfiscal.inf.br/nfe}uCom')
                if u_com is None:
                    u_com = prod.find('.//uCom')
                if u_com is not None:
                    produto['unidade'] = u_com.text
                
                # Quantidade
                q_com = prod.find('.//{http://www.portalfiscal.inf.br/nfe}qCom')
                if q_com is None:
                    q_com = prod.find('.//qCom')
                if q_com is not None:
                    try:
                        produto['quantidade'] = float(q_com.text)
                    except:
                        produto['quantidade'] = 0
                
                # Valor unitário
                v_un_com = prod.find('.//{http://www.portalfiscal.inf.br/nfe}vUnCom')
                if v_un_com is None:
                    v_un_com = prod.find('.//vUnCom')
                if v_un_com is not None:
                    try:
                        produto['valor_unitario'] = float(v_un_com.text)
                    except:
                        produto['valor_unitario'] = 0
                
                # Valor total do produto
                v_prod = prod.find('.//{http://www.portalfiscal.inf.br/nfe}vProd')
                if v_prod is None:
                    v_prod = prod.find('.//vProd')
                if v_prod is not None:
                    try:
                        produto['valor_total'] = float(v_prod.text)
                    except:
                        produto['valor_total'] = produto.get('valor_unitario', 0) * produto.get('quantidade', 0)
                
                produtos.append(produto)
        
        return produtos
    
    def _extrair_totais(self, root: ET.Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """Extrai totais da NF-e."""
        totais = {
            'valor_total': 0,
            'valor_produtos': 0,
            'valor_impostos': 0
        }
        
        total = root.find('.//{http://www.portalfiscal.inf.br/nfe}total')
        if total is None:
            total = root.find('.//total')
        
        if total is not None:
            icms_tot = total.find('.//{http://www.portalfiscal.inf.br/nfe}ICMSTot')
            if icms_tot is None:
                icms_tot = total.find('.//ICMSTot')
            
            if icms_tot is not None:
                v_nf = icms_tot.find('.//{http://www.portalfiscal.inf.br/nfe}vNF')
                if v_nf is None:
                    v_nf = icms_tot.find('.//vNF')
                if v_nf is not None:
                    try:
                        totais['valor_total'] = float(v_nf.text)
                    except:
                        pass
                
                v_prod = icms_tot.find('.//{http://www.portalfiscal.inf.br/nfe}vProd')
                if v_prod is None:
                    v_prod = icms_tot.find('.//vProd')
                if v_prod is not None:
                    try:
                        totais['valor_produtos'] = float(v_prod.text)
                    except:
                        pass
        
        return totais
    
    def _detectar_tipo_movimentacao(
        self,
        root: ET.Element,
        ns: Dict[str, str],
        empresa_id_override: Optional[int]
    ) -> str:
        """Detecta se é ENTRADA ou SAIDA baseado no CNPJ do emitente."""
        emitente = self._extrair_emitente(root, ns)
        cnpj_emitente = emitente.get('cnpj')
        
        if not cnpj_emitente:
            return "SAIDA"  # Default
        
        # Normalizar CNPJ
        cnpj_normalizado = normalizar_cnpj(cnpj_emitente)
        
        # Buscar empresas cadastradas
        empresas = self.db.query(models.Empresa).all()
        for empresa in empresas:
            # Verificar se o CNPJ do emitente é de alguma empresa cadastrada
            # (isso indicaria que é uma NF de SAÍDA - emitida por nós)
            # Por enquanto, assumir que se não conseguirmos identificar, é ENTRADA
            pass
        
        # Se empresa_id_override foi fornecido, usar lógica diferente
        if empresa_id_override:
            empresa = self.db.query(models.Empresa).filter(models.Empresa.id == empresa_id_override).first()
            if empresa:
                # Verificar se CNPJ do emitente corresponde à empresa
                # Se sim, é SAÍDA (emitida por nós)
                # Se não, é ENTRADA (recebida de fornecedor)
                return "SAIDA"  # Simplificado por enquanto
        
        # Por padrão, se não conseguir identificar, assumir SAÍDA
        # (mais comum no contexto do sistema)
        return "SAIDA"
    
    def _identificar_empresa(
        self,
        root: ET.Element,
        ns: Dict[str, str],
        empresa_id_override: Optional[int]
    ) -> Optional[int]:
        """Identifica empresa pelo CNPJ do emitente ou destinatário."""
        if empresa_id_override:
            return empresa_id_override
        
        emitente = self._extrair_emitente(root, ns)
        cnpj_emitente = emitente.get('cnpj')
        
        if cnpj_emitente:
            empresa_id = EmpresaService.identificar_empresa_por_cnpj(self.db, cnpj_emitente)
            if empresa_id:
                return empresa_id
        
        # Se não encontrou, usar padrão
        return EmpresaService.get_empresa_id(self.db, "HIGIPLAS")
    
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
            codigo = produto_data.get('codigo', '')
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
