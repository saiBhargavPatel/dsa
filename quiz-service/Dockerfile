FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Honor Render's PORT env var (defaults to 4003 for local runs).
EXPOSE 4003
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-4003}"]
