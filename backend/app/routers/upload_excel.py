# backend/app/routers/upload_excel.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO

# Importações necessárias
from app.db.connection import get_db
from app.crud import produto as crud_produto
from app.schemas import produto as schemas_produto
from app.schemas import usuario as schemas_usuario
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/upload-excel", status_code=status.HTTP_200_OK)
async def upload_excel_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas_usuario.Usuario = Depends(get_current_user)
):
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="Arquivo deve ser Excel (.xls ou .xlsx)")

    contents = await file.read()
    try:
        # Substitui valores vazios por None para evitar erros com NaN
        df = pd.read_excel(contents).fillna(value=pd.NA)
        # Garante que os nomes das colunas estão em minúsculo para facilitar a busca
        df.columns = df.columns.str.lower()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler Excel: {str(e)}")

    # Colunas obrigatórias para criar/atualizar um produto.
    required_cols = {"codigo", "nome", "categoria", "preco_venda", "unidade_medida"}
    if not required_cols.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"O Excel deve conter as colunas: {', '.join(required_cols)}")

    # --- INÍCIO DA SEÇÃO DE DEPURAÇÃO ---
    print("--- INICIANDO PROCESSAMENTO DE UPLOAD ---")
    print(f"Arquivo recebido: {file.filename}")
    print(f"Total de linhas encontradas no Excel: {len(df)}")
    # --- FIM DA SEÇÃO DE DEPURAÇÃO ---

    erros = []
    processados = 0

    for index, row in df.iterrows():
        # --- DEPURAÇÃO DENTRO DO LOOP ---
        print("\n" + "="*50)
        print(f"[DEBUG] Processando linha do Excel nº: {index + 2}")
        print(f"[DEBUG] DADOS DA LINHA BRUTA:\n{row.to_dict()}")
        # --- FIM DA DEPURAÇÃO DENTRO DO LOOP ---

        try:
            # Validação para pular linhas completamente vazias
            if row.isnull().all():
                print("[DEBUG] Linha vazia detectada. Pulando...")
                continue

            # Validação para garantir que os campos obrigatórios não são nulos na linha atual
            for col in required_cols:
                if pd.isna(row.get(col)):
                    raise ValueError(f"A coluna obrigatória '{col}' está vazia.")

            # Constrói o objeto do produto a partir da linha do Excel
            produto_data = schemas_produto.ProdutoCreate(
                codigo=str(row["codigo"]),
                nome=str(row["nome"]),
                categoria=str(row["categoria"]),
                preco_venda=float(row["preco_venda"]),
                unidade_medida=str(row["unidade_medida"]),
                quantidade_em_estoque=int(row.get("estoque")) if pd.notna(row.get("estoque")) else 0,
                # Campos opcionais com tratamento para valores nulos (NA)
                descricao=str(row.get("descricao")) if pd.notna(row.get("descricao")) else None,
                preco_custo=float(row.get("preco_custo")) if pd.notna(row.get("preco_custo")) else None,
                estoque_minimo=int(row.get("estoque_minimo")) if pd.notna(row.get("estoque_minimo")) else 0,
                data_validade=pd.to_datetime(row.get("data_validade")).date() if pd.notna(row.get("data_validade")) else None,
            )
            
            print(f"[DEBUG] Objeto Pydantic criado com sucesso. Enviando para o CRUD...")
            
            # Chama a função "upsert"
            crud_produto.create_or_update_produto(db=db, produto_data=produto_data, empresa_id=current_user.empresa_id)
            processados += 1
            print(f"[DEBUG] Linha {index + 2} processada com SUCESSO. (Total processados: {processados})")

        except Exception as e:
            error_message = f"Erro na linha {index + 2} (Produto código: '{row.get('codigo', 'N/A')}'): {str(e)}"
            print(f"[ERRO] {error_message}")
            erros.append(error_message)

    # --- DEPURAÇÃO FINAL ---
    print("\n" + "="*50)
    print("--- FIM DO PROCESSAMENTO DO ARQUIVO ---")
    print(f"Total de produtos processados com sucesso: {processados}")
    print(f"Total de erros encontrados: {len(erros)}")
    if erros:
        print("Resumo dos erros:")
        for err in erros:
            print(f"  - {err}")
    print("="*50)
    # --- FIM DA DEPURAÇÃO FINAL ---

    if erros:
        return {"message": f"{processados} produtos processados com erros. Verifique o log do servidor para detalhes.", "processados": processados, "erros": erros}

    return {"message": "Todos os produtos foram processados com sucesso!", "processados": processados}