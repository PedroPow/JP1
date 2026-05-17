FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (otimiza o cache do build)
COPY requirements.txt ./

# Instala as dependências de forma limpa
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do bot (bot.py, .env, etc.)
COPY . .

# Comando para executar o bot
CMD ["python", "bot.py"]