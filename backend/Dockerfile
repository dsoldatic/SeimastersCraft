# Koristimo službenu Python sliku s Debian bazom (bullseye) umjesto slim
FROM python:3.11-bullseye

# 1. Postavite env varijable za Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 2. Instalirajte sistemske ovisnosti s cleanup-om
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-distutils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Kreirajte radni direktorij
WORKDIR /app

# 4. Prvo kopirajte requirements.txt za bolje caching
COPY requirements.txt .

# 5. Instalirajte Python ovisnosti
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 6. Kopirajte ostatak aplikacije (izuzev .dockerignore stavki)
COPY . .

# 7. Postavite port i healthcheck
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 8. Pokrenite aplikaciju
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]