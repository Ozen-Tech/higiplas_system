FROM python:3.11-slim

# Define a variável de ambiente PYTHONPATH
# Isso diz ao Python: "Além das pastas padrão, olhe também dentro de /code para encontrar módulos."
ENV PYTHONPATH="/code"

WORKDIR /code

# Instala as dependências PRIMEIRO para aproveitar o cache do Docker
COPY requirements.txt /code/requirements.txt
RUN pip install --timeout=100 --no-cache-dir --upgrade -r /code/requirements.txt

# Copia todo o resto da aplicação
COPY . /code

# (O CMD ou ENTRYPOINT que você tinha aqui pode ser removido, pois usaremos o start.sh da Render)