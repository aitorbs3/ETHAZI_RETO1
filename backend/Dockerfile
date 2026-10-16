# Apache Derby de este proyecto está compilado para Java 19 o superior.
# Debian trixie incluye OpenJDK 21, necesario para JDBC desde JPype.
FROM python:3.11-slim-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
