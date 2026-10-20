FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    OUTPUT_DIR=/app/output

WORKDIR /app

# Dependencies first, so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt "setuptools<81"

COPY . .
RUN mkdir -p /app/output && chmod +x /app/entrypoint.sh

EXPOSE 6800
ENTRYPOINT ["/app/entrypoint.sh"]