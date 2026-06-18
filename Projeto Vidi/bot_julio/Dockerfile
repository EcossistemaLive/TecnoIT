FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (asyncpg precisa de gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python primeiro (cache de layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Usuário não-root (segurança)
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Porta exposta pelo uvicorn
EXPOSE 8080

# Iniciar FastAPI via uvicorn (2 workers para aproveitar multi-core do VPS 20)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
