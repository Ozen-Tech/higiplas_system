# backend/manage.py

import typer
import getpass
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.crud import usuario as crud_usuario
from app.schemas import usuario as schemas_usuario
from app.db import models

# Cria a nossa aplicação de linha de comando
cli_app = typer.Typer()

@cli_app.command()
def create_user():
    """
    Cria um novo usuário no sistema de forma interativa.
    """
    print("--- 🚀 Criando Novo Usuário ---")
    
    # Abre uma sessão com o banco de dados
    db: Session = next(get_db())
    
    try:
        # Pede as informações de forma interativa
        nome = typer.prompt("Nome completo do usuário")
        email = typer.prompt("E-mail do usuário")
        
        # Validação de e-mail existente
        if crud_usuario.get_user_by_email(db, email=email):
            print(f"\n❌ Erro: O e-mail '{email}' já está em uso.")
            raise typer.Abort()

        # Usando getpass para que a senha não seja exibida na tela
        password = getpass.getpass("Digite a senha: ")
        password_confirm = getpass.getpass("Confirme a senha: ")

        if password != password_confirm:
            print("\n❌ Erro: As senhas não conferem.")
            raise typer.Abort()

        # Permite a escolha do perfil (você pode customizar aqui)
        perfil = typer.prompt(
            "Qual o perfil do usuário?", 
            type=click.Choice(list(schemas_usuario.PerfilUsuario)), # Usando a Enum
            default=schemas_usuario.PerfilUsuario.OPERADOR.value,
            show_choices=True
        )

        empresa_id_str = typer.prompt("ID da Empresa à qual o usuário pertence", default="1")
        empresa_id = int(empresa_id_str)
        
        user_in = schemas_usuario.UsuarioCreate(
            nome=nome,
            email=email,
            password=password,
            perfil=perfil,
            empresa_id=empresa_id,
        )

        # Chama a função do CRUD para criar o usuário
        user = crud_usuario.create_user(db=db, user_in=user_in, empresa_id=empresa_id)
        
        print("\n--- ✅ Sucesso! ---")
        print(f"Usuário '{user.nome}' criado com o e-mail '{user.email}' e perfil '{user.perfil}'.")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")
    finally:
        db.close()

# Você pode adicionar mais comandos aqui no futuro. Por exemplo, um para listar usuários:
@cli_app.command()
def list_users():
    """Lista todos os usuários cadastrados."""
    db: Session = next(get_db())
    try:
        users = db.query(models.Usuario).all()
        if not users:
            print("Nenhum usuário encontrado.")
            return

        print("\n--- 👥 Lista de Usuários ---")
        for user in users:
            print(f"- ID: {user.id}, Nome: {user.nome}, E-mail: {user.email}, Perfil: {user.perfil}, Ativo: {user.is_active}")
        print("-" * 20)

    finally:
        db.close()

# Ponto de entrada para o Typer
if __name__ == "__main__":
    # Import necessário para a Enum de PerfilUsuario funcionar com Typer
    import click 
    cli_app()