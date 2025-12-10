# 1. Usamos Python 3.12 slim como base
FROM python:3.12-slim

# 2. Instalar Java 11 (para PySpark)
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get clean

# 3. Configurar variables de entorno de Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# 4. Crear carpeta de trabajo en el contenedor
WORKDIR /app

# 5. Copiar todo el proyecto al contenedor
COPY . /app

# 6. Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 7. Comando por defecto al ejecutar el contenedor
CMD ["python", "src/benchmark.py"]
