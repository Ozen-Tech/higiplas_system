#!/usr/bin/env python3
"""
Script para criar todas as tabelas do banco de dados usando SQLAlchemy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import engine, Base
from app.db.models import *  # Importa todos os modelos

def create_all_tables():
    """Cria todas as tabelas definidas nos modelos"""
    try:
        print("Criando todas as tabelas...")
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tabelas criadas: {tables}")
        
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_all_tables()
    sys.exit(0 if success else 1)