# Usar a imagem oficial do Python
FROM python:3.12-slim

# Definir variáveis de ambiente para evitar arquivos .pyc e logs em buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho no container
WORKDIR /app

# Instalar dependências do sistema necessárias para o psycopg2 e outras libs
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar os arquivos de requisitos e instalar dependências do Python
# Criarei um requirements.txt básico se ele não existir
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar o restante do código para o container
COPY . /app/

# Comando padrão para rodar a aplicação (usaremos o entrypoint no compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
