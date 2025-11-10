FROM python:3.12-slim

WORKDIR /app

# Instalar uv
RUN pip install --no-cache-dir uv

# Copiar arquivos de dependências
COPY pyproject.toml .
COPY uv.lock* ./

# Instalar dependências do projeto usando uv
RUN uv sync

# Copiar o resto do projeto
COPY . .

# Comando padrão (usa init.py para migrations + seed + app)
CMD ["tail", "-f", "/dev/null"]
