# backend/manage.py

import typer
import getpass
from sqlalchemy.orm import Session
import json
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
            default=schemas_usuario.PerfilUsuario.VENDEDOR.value,
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

@cli_app.command()
def seed_historical_data():
    """
    Lê o 'dados_historicos_vendas.json' e o insere na tabela 'vendas_historicas'.
    Este comando é idempotente: ele verifica se um registro já existe antes de inserir,
    portanto é seguro rodá-lo múltiplas vezes sem criar duplicatas.
    """
    json_file = "app/dados_historicos_vendas.json"
    print(f"\n--- 🌱 Iniciando o 'seeding' do banco com o arquivo: {json_file} ---")

    db: Session = next(get_db())
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("❌ Arquivo JSON está vazio. Nenhuma ação tomada.")
            raise typer.Abort()

        print(f"Encontrados {len(data)} registros no JSON. Verificando e inserindo no banco...")
        
        # Pega todos os IDs existentes do banco de uma vez para otimizar
        ids_existentes = {result[0] for result in db.query(models.VendaHistorica.ident_antigo).all()}
        
        itens_para_adicionar = []
        existentes = 0
        
        for item in data:
            ident_antigo = item.get("ident_antigo")
            if ident_antigo in ids_existentes:
                existentes += 1
                continue # Pula para o próximo item
            
            # Adiciona apenas se não existir E evita duplicatas do próprio JSON
            if ident_antigo not in (i.ident_antigo for i in itens_para_adicionar):
                novo_registro = models.VendaHistorica(**item)
                itens_para_adicionar.append(novo_registro)

        if not itens_para_adicionar:
            print("Nenhum registro novo para adicionar. O banco já está atualizado.")
        else:
            db.bulk_save_objects(itens_para_adicionar)
            db.commit()
            print(f"{len(itens_para_adicionar)} novos registros foram adicionados.")

        print("\n--- ✅ Seeding concluído! ---")
        print(f"Total de registros novos inseridos: {len(itens_para_adicionar)}")
        print(f"Total de registros que já existiam (ignorados): {existentes}")

    except FileNotFoundError:
        print(f"❌ ERRO: O arquivo '{json_file}' não foi encontrado.")
        raise typer.Abort()
    except Exception as e:
        print(f"❌ Ocorreu um erro durante o seeding: {e}")
        db.rollback()
    finally:
        db.close()

# Ponto de entrada para o Typer
if __name__ == "__main__":
    # Import necessário para a Enum de PerfilUsuario funcionar com Typer
    import click 
    cli_app()