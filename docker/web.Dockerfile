FROM python:3.11-slim

ENV NODE_VERSION=18.19.1

# Instala curl, extrator e dependências mínimas
RUN apt-get update && apt-get install -y curl xz-utils && \
    curl -fsSL https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz | tar -xJ -C /usr/local --strip-components=1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN npm install && npm run build:prod

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
