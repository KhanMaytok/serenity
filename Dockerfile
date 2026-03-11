# Usar una imagen oficial de Python
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Puerto en el que corre Django
EXPOSE 8000

# Usar el script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando por defecto para correr el servidor
CMD ["gunicorn", "seren_project.wsgi:application", "--bind", "0.0.0.0:8000"]
