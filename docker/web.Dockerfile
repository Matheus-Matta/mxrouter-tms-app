FROM ubuntu:22.04

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

# Instala Python + Node.js + dependências
RUN apt-get install -y python3.11 python3-pip nodejs npm curl git build-essential && \
    ln -sf python3.11 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    
# Define diretório de trabalho
WORKDIR /app

# Instala dependências Python
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do código
COPY . .

# Instala dependências do Node (ex: Tailwind, etc.)
RUN npm install && npm run build:prod

# Script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Expõe a porta do Gunicorn
EXPOSE 8000

# Comando padrão
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
