FROM eclipse-temurin:17-jdk

# Instalar Python 3.12 y venv
RUN apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3-pip curl && \
    apt-get clean

WORKDIR /app

# Crear venv y activarlo
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements e instalar dependencias dentro del venv
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

CMD ["python", "src/benchmark.py"]
