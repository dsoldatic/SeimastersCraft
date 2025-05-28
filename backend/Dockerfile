# 1. baza sa distutils
FROM python:3.11-slim

# 2. instaliraj ono što ti fali u slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      python3-distutils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. ostatak
COPY . .

EXPOSE 8000

# 5. moramo ekspandirati $PORT, zato
CMD ["sh","-c","uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]