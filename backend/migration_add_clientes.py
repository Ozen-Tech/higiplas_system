#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração para adicionar as novas tabelas e campos relacionados a clientes.
Execute este script após atualizar os modelos.
"""

import sys
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.db.connection import engine
from app.db.models import Base

def run_migration():
    """Executa a migração do banco de dados."""
    
    print("Iniciando migração do banco de dados...")
    
    try:
        # Cria as novas tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Novas tabelas criadas com sucesso!")
        
        # Executa alterações nas tabelas existentes
        with engine.connect() as conn:
            # Adiciona novos campos na tabela orcamentos
            migration_queries = [
                # Remove a coluna nome_cliente se existir (será substituída por cliente_id)
                "ALTER TABLE orcamentos DROP COLUMN IF EXISTS nome_cliente;",
                
                # Adiciona novos campos na tabela orcamentos
                "ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS cliente_id INTEGER;",
                "ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS condicao_pagamento VARCHAR(255);",
                "ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS preco_minimo DECIMAL(10,2);",
                "ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS preco_maximo DECIMAL(10,2);",
                "ALTER TABLE orcamentos ADD COLUMN IF NOT EXISTS numero_nf VARCHAR(100);",
                
                # Adiciona foreign key para cliente_id
                "ALTER TABLE orcamentos ADD CONSTRAINT IF NOT EXISTS fk_orcamentos_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id);",
            ]
            
            for query in migration_queries:
                try:
                    conn.execute(text(query))
                    print(f"✅ Executado: {query[:50]}...")
                except Exception as e:
                    print(f"⚠️  Aviso ao executar query: {e}")
                    # Continua mesmo com erros (pode ser que a coluna já exista)
            
            conn.commit()
            print("✅ Migração de campos concluída!")
        
        print("\n🎉 Migração concluída com sucesso!")
        print("\nPróximos passos:")
        print("1. Verifique se todas as tabelas foram criadas corretamente")
        print("2. Popule a tabela 'clientes' com dados existentes se necessário")
        print("3. Atualize os orçamentos existentes para referenciar clientes")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False
    
    return True

def create_sample_data():
    """Cria dados de exemplo para testar o sistema."""
    from app.db.connection import get_db
    from app.db import models
    
    db = next(get_db())
    
    try:
        # Verifica se já existem empresas
        empresa_higiplas = db.query(models.Empresa).filter(
            models.Empresa.nome == "Higiplas"
        ).first()
        
        empresa_higitec = db.query(models.Empresa).filter(
            models.Empresa.nome == "Higitec"
        ).first()
        
        if not empresa_higiplas:
            empresa_higiplas = models.Empresa(
                nome="Higiplas",
                cnpj="12.345.678/0001-90",
                endereco="Rua das Empresas, 123",
                telefone="(11) 1234-5678",
                email="contato@higiplas.com.br"
            )
            db.add(empresa_higiplas)
        
        if not empresa_higitec:
            empresa_higitec = models.Empresa(
                nome="Higitec",
                cnpj="98.765.432/0001-10",
                endereco="Av. Tecnologia, 456",
                telefone="(11) 9876-5432",
                email="contato@higitec.com.br"
            )
            db.add(empresa_higitec)
        
        db.commit()
        db.refresh(empresa_higiplas)
        db.refresh(empresa_higitec)
        
        # Cria clientes de exemplo
        clientes_exemplo = [
            {
                "razao_social": "Cliente Exemplo Ltda",
                "cnpj": "11.222.333/0001-44",
                "endereco": "Rua do Cliente, 789",
                "email": "contato@clienteexemplo.com.br",
                "telefone": "(11) 1111-2222",
                "empresa_id": empresa_higiplas.id,
                "status_pagador": "BOM"
            },
            {
                "razao_social": "Outro Cliente S.A.",
                "cnpj": "22.333.444/0001-55",
                "endereco": "Av. Outro Cliente, 321",
                "email": "contato@outrocliente.com.br",
                "telefone": "(11) 3333-4444",
                "empresa_id": empresa_higitec.id,
                "status_pagador": "REGULAR"
            }
        ]
        
        for cliente_data in clientes_exemplo:
            existing_cliente = db.query(models.Cliente).filter(
                models.Cliente.cnpj == cliente_data["cnpj"]
            ).first()
            
            if not existing_cliente:
                cliente = models.Cliente(**cliente_data)
                db.add(cliente)
        
        db.commit()
        print("✅ Dados de exemplo criados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DO BANCO DE DADOS ===")
    print("Este script irá:")
    print("1. Criar as novas tabelas (clientes, historico_pagamentos, produtos_mais_vendidos)")
    print("2. Adicionar novos campos na tabela orcamentos")
    print("3. Criar dados de exemplo")
    print()
    
    resposta = input("Deseja continuar? (s/N): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        if run_migration():
            print("\n=== CRIANDO DADOS DE EXEMPLO ===")
            create_sample_data()
        else:
            print("❌ Migração falhou. Não criando dados de exemplo.")
    else:
        print("Migração cancelada.")