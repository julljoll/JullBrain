FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY iniciar_conversion.bat .

RUN mkdir -p normativas_pdf formatos_word normativas_rag formatos_rag normativas_chunks .conversion_cache

ENTRYPOINT ["python", "convert_normativas.py"]
