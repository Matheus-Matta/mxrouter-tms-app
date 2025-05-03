FROM python:3.11-slim

# Instala dependências mínimas
RUN apt-get update && apt-get install -y curl gnupg

# Copia o script de instalação local
COPY ./setup_18.x /tmp/setup_node.sh

# Executa o script para configurar o repositório do Node
RUN bash /tmp/setup_node.sh && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do código
COPY . .

# Instala dependências Node (Tailwind etc.)
RUN npm install && npm run build:prod

# Entrypoint para execução
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
