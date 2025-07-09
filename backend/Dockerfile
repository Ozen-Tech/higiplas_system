# /backend/Dockerfile

# 1. Use uma imagem Python oficial e leve
FROM python:3.11-slim

# 2. Defina o diretório de trabalho dentro do container
WORKDIR /code

# 3. Copie o arquivo de dependências PRIMEIRO
# Correção: Copie a partir da raiz do contexto de build (que é a pasta 'backend')
COPY requirements.txt /code/requirements.txt

# 4. Instale as dependências
RUN pip install --timeout=100 --no-cache-dir --upgrade -r /code/requirements.txt
# 5. Copie o resto do código da sua aplicação
# Correção: Copie tudo da raiz do contexto (a pasta 'backend') para o diretório de trabalho
COPY . /code

# 6. Exponha a porta que o Uvicorn usará
EXPOSE 8000

# 7. Comando para iniciar a aplicação
#    --host 0.0.0.0 é CRUCIAL para que a API seja acessível de fora do container.
CMD ["/code/start.sh"]
