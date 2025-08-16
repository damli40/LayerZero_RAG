FROM python:3.10-slim

# Prevent Python from buffering logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install supervisor and curl for healthchecks
RUN apt-get update && apt-get install -y supervisor curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Ensure startup script is executable
RUN chmod +x /app/start.sh

# Create an empty .env so slowapi's Config(".env") does not fail
RUN touch /app/.env

# Expose FastAPI port
EXPOSE 8000

# Basic healthcheck hitting FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["./start.sh"]
