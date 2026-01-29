# Hafif Python 3.11 image'ı kullan (Railway için ideal)
FROM python:3.11-slim

# Gerekli sistem paketleri + cloudflared binary indir
RUN apt-get update -y && \
    apt-get install -y wget && \
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared && \
    chmod +x /usr/local/bin/cloudflared && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Tüm dosyaları kopyala (start.py, requirements.txt vs.)
COPY . .

# Python bağımlılıklarını kur
RUN pip install --no-cache-dir -r requirements.txt

# Botu başlat
CMD ["python", "start.py"]