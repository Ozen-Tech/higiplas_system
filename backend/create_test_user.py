#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_db
from app.db.models import Usuario
from app.core.hashing import get_password_hash

def create_test_user():
    print("🔧 Criando usuário de teste...")
    
    try:
        db = next(get_db())
        
        # Verificar se já existe
        existing_user = db.query(Usuario).filter(Usuario.email == "test@higiplas.com").first()
        if existing_user:
            print("✅ Usuário de teste já existe!")
            print(f"   Email: test@higiplas.com")
            print(f"   Senha: test123")
            return
        
        # Criar novo usuário
        hashed_password = get_password_hash("test123")
        new_user = Usuario(
            nome="Usuário Teste",
            email="test@higiplas.com",
            hashed_password=hashed_password,
            perfil="ADMIN"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("✅ Usuário de teste criado com sucesso!")
        print(f"   Email: test@higiplas.com")
        print(f"   Senha: test123")
        print(f"   ID: {new_user.id}")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário de teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_user()