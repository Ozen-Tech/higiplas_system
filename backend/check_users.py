#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.connection import get_db
from app.db.models import Usuario

def check_users():
    print("🔍 Verificando usuários no banco de dados...")
    
    try:
        db = next(get_db())
        users = db.query(Usuario).all()
        
        print(f"📊 Total de usuários encontrados: {len(users)}")
        
        if users:
            print("\n👥 Usuários cadastrados:")
            for i, user in enumerate(users[:5], 1):  # Mostra até 5 usuários
                print(f"   {i}. Email: {user.email}")
                print(f"      Nome: {user.nome}")
                print(f"      Perfil: {user.perfil}")
                print(f"      Ativo: {user.ativo}")
                print("   ---")
        else:
            print("❌ Nenhum usuário encontrado no banco de dados.")
            print("💡 Você precisa criar um usuário primeiro.")
            
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users()