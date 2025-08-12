#!/usr/bin/env python3

import sys
sys.path.append('/Users/ozen/higiplas_system/backend')

from app.db.connection import get_db
from app.db.models import Usuario, Empresa
from sqlalchemy.orm import Session

def fix_test_user():
    db = next(get_db())
    
    try:
        # Buscar o usuário test@higiplas.com
        user = db.query(Usuario).filter(Usuario.email == "test@higiplas.com").first()
        
        if not user:
            print("Usuário test@higiplas.com não encontrado")
            return
        
        print(f"Usuário encontrado: {user.email}")
        print(f"Empresa ID atual: {user.empresa_id}")
        
        # Buscar uma empresa existente ou criar uma
        empresa = db.query(Empresa).first()
        
        if not empresa:
            # Criar uma empresa se não existir
            empresa = Empresa(nome="Higiplas", cnpj="12345678000123")
            db.add(empresa)
            db.commit()
            db.refresh(empresa)
            print(f"Empresa criada: {empresa.nome} (ID: {empresa.id})")
        else:
            print(f"Empresa existente: {empresa.nome} (ID: {empresa.id})")
        
        # Atualizar o usuário com a empresa_id
        user.empresa_id = empresa.id
        db.commit()
        
        print(f"✅ Usuário {user.email} atualizado com empresa_id: {user.empresa_id}")
        
    except Exception as e:
        print(f"Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_test_user()