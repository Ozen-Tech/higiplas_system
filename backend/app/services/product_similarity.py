from typing import List, Dict, Any, Optional
from fuzzywuzzy import fuzz, process
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.crud.produto import get_produtos
import re

class ProductSimilarityService:
    """Serviço para busca de produtos por similaridade de nomes"""
    
    def __init__(self):
        self.products_cache = None
        self.product_names_cache = None
    
    def _load_products(self, db: Session, empresa_id: int) -> List[Dict[str, Any]]:
        """Carrega todos os produtos do banco de dados para uma empresa específica"""
        if self.products_cache is None:
            produtos = get_produtos(db, empresa_id)
            self.products_cache = [
                {
                    'id': p.id,
                    'nome': p.nome,
                    'codigo': p.codigo,
                    'categoria': p.categoria,
                    'unidade_medida': p.unidade_medida,
                    'preco_venda': float(p.preco_venda) if p.preco_venda else 0,
                    'descricao': p.descricao
                }
                for p in produtos
            ]
            self.product_names_cache = {p['nome']: p for p in self.products_cache}
        
        return self.products_cache
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        if not text:
            return ""
        
        # Remove caracteres especiais e converte para maiúsculo
        normalized = re.sub(r'[^A-Za-z0-9\s]', ' ', text.upper())
        # Remove espaços extras
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave importantes do texto"""
        normalized = self._normalize_text(text)
        words = normalized.split()
        
        # Remove palavras muito pequenas ou comuns
        stop_words = {'DE', 'DA', 'DO', 'COM', 'SEM', 'PARA', 'EM', 'NA', 'NO', 'E', 'OU'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def find_similar_products(
        self, 
        search_name: str, 
        db: Session,
        empresa_id: int,
        limit: int = 10,
        min_similarity: int = 60
    ) -> List[Dict[str, Any]]:
        """Encontra produtos similares baseado no nome"""
        
        products = self._load_products(db, empresa_id)
        
        if not search_name or not products:
            return []
        
        # Normaliza o termo de busca
        normalized_search = self._normalize_text(search_name)
        search_keywords = self._extract_keywords(search_name)
        
        # Lista para armazenar resultados com scores
        results = []
        
        for product in products:
            product_name = product['nome']
            normalized_product = self._normalize_text(product_name)
            
            # Calcula diferentes tipos de similaridade
            scores = {
                'ratio': fuzz.ratio(normalized_search, normalized_product),
                'partial_ratio': fuzz.partial_ratio(normalized_search, normalized_product),
                'token_sort_ratio': fuzz.token_sort_ratio(normalized_search, normalized_product),
                'token_set_ratio': fuzz.token_set_ratio(normalized_search, normalized_product)
            }
            
            # Score baseado em palavras-chave
            product_keywords = self._extract_keywords(product_name)
            keyword_matches = sum(1 for kw in search_keywords if kw in product_keywords)
            keyword_score = (keyword_matches / len(search_keywords) * 100) if search_keywords else 0
            
            # Score final (média ponderada)
            final_score = (
                scores['ratio'] * 0.2 +
                scores['partial_ratio'] * 0.2 +
                scores['token_sort_ratio'] * 0.3 +
                scores['token_set_ratio'] * 0.2 +
                keyword_score * 0.1
            )
            
            if final_score >= min_similarity:
                results.append({
                    **product,
                    'similarity_score': round(final_score, 2),
                    'match_details': {
                        'ratio': scores['ratio'],
                        'partial_ratio': scores['partial_ratio'],
                        'token_sort_ratio': scores['token_sort_ratio'],
                        'token_set_ratio': scores['token_set_ratio'],
                        'keyword_score': round(keyword_score, 2),
                        'keyword_matches': keyword_matches,
                        'total_keywords': len(search_keywords)
                    }
                })
        
        # Ordena por score de similaridade (maior primeiro)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:limit]
    
    def find_best_match(
        self, 
        search_name: str, 
        db: Session,
        empresa_id: int,
        min_similarity: int = 80
    ) -> Optional[Dict[str, Any]]:
        """Encontra a melhor correspondência para um produto"""
        
        similar_products = self.find_similar_products(
            search_name, db, empresa_id, limit=1, min_similarity=min_similarity
        )
        
        return similar_products[0] if similar_products else None
    
    def batch_find_similar(
        self,
        product_names: List[str],
        db: Session,
        empresa_id: int,
        limit_per_product: int = 5,
        min_similarity: int = 60
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Encontra produtos similares para uma lista de nomes"""
        
        results = {}
        
        for name in product_names:
            similar = self.find_similar_products(
                name, db, empresa_id, limit=limit_per_product, min_similarity=min_similarity
            )
            results[name] = similar
        
        return results
    
    def clear_cache(self):
        """Limpa o cache de produtos"""
        self.products_cache = None
        self.product_names_cache = None

# Instância global do serviço
product_similarity_service = ProductSimilarityService()