FROM node:20-slim

# Instala Python 3 e dependências mínimas para o motor analítico
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia arquivos de dependência
COPY package*.json ./
RUN npm install --production

# Copia código do bot e motor analítico
COPY . .

# Cria diretórios para logs e credenciais
RUN mkdir -p logs auth_info

ENV PYTHONIOENCODING=utf-8
ENV NODE_ENV=production

CMD ["npm", "start"]
