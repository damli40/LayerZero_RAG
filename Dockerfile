FROM python:3.10-slim

# Prevent Python from buffering logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

COPY . .

CMD ["./start.sh"]
