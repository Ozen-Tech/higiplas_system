# Use uma imagem base do Python
FROM python:3.11-slim

# Defina o diretório de trabalho no container
WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code"

# Copie o arquivo de dependências PRIMEIRO para aproveitar o cache do Docker
COPY ./backend/requirements.txt /code/requirements.txt

# Instale as dependências
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Agora, copie o conteúdo da pasta 'backend' para o diretório de trabalho
COPY ./backend/ /code/

# Exponha a porta que a aplicação vai rodar
EXPOSE 8000

# Comando para rodar a aplicação.
# Uvicorn vai procurar por 'app.main' dentro do WORKDIR (/code)
CMD ["/bin/sh", "-c", "python -m app.prestart && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]