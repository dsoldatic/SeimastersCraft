# koristimo službeni Python 3.11 image
FROM python:3.11-slim

# radni direktorij
WORKDIR /app

# kopiraj samo requirements pa instaliraj (iskoristi Docker cache)
COPY requirements.txt .

# instaliraj sve dependencyje
RUN pip install --no-cache-dir -r requirements.txt

# kopiraj ostatak koda
COPY . .

# expose porta (Railway automatski preusmjeri $PORT okoline)
EXPOSE 8000

# komanda za startanje
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]