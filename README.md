# Seren — Groq + Embeddings Locales (100% Gratuito)

Seren es un sistema de chat inteligente con memoria a largo plazo (RAG) diseñado para ser 100% gratuito y eficiente.

**Stack Tecnológico:**
- **Chat**: Groq API — llama-3.3-70b-versatile (Alta velocidad, costo $0).
- **Embeddings**: `sentence-transformers` local — procesamiento local sin costo de API.
- **Base de datos**: PostgreSQL + `pgvector` para búsqueda semántica.
- **Backend**: Django.
- **Configuración**: Python Decouple para manejo seguro de variables de entorno.

## 🚀 Inicio Rápido con Docker (Recomendado)

La forma más rápida de empezar es usando Docker, que ya incluye una base de datos con soporte para vectores.

1.  **Variables de entorno**:
    ```bash
    cp .env.example .env
    # Edita el archivo .env y pega tu GROQ_API_KEY
    ```

2.  **Levantar el proyecto**:
    ```bash
    docker-compose up --build
    ```

Abre → [http://localhost:8000](http://localhost:8000)

---

## 🛠 Instalación Manual

Si prefieres no usar Docker, sigue estos pasos:

### 1. Requisitos Previos
- PostgreSQL con la extensión [pgvector](https://github.com/pgvector/pgvector) instalada.
- Python 3.11+.

### 2. Configuración de Base de Datos
```sql
CREATE DATABASE seren_db;
-- Asegúrate de que el usuario tenga permisos
```

### 3. Setup de Python
1. **Crear entorno virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
   *Nota: La instalación inicial de torch + sentence-transformers puede ocupar ~1.5GB.*

### 4. Variables de Entorno
Crea un archivo `.env` basado en `.env.example`:
```env
DJANGO_SECRET_KEY=tu_clave_secreta
DEBUG=True
GROQ_API_KEY=gsk_...
DB_NAME=seren_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Migraciones y Ejecución
```bash
python manage.py migrate
python manage.py runserver
```

---

## 🧠 Funcionamiento de la Memoria (RAG)

Seren utiliza un modelo local de embeddings para procesar tus mensajes sin enviarlos a APIs externas de terceros para la vectorización.

**Modelo utilizado:** `paraphrase-multilingual-MiniLM-L12-v2`
- ✅ Optimizado para **español** y otros idiomas.
- ✅ Ligero: 384 dimensiones.
- ✅ Ejecución rápida en CPU.
- ✅ Descarga automática (~90MB) en el primer uso.

Al enviar tu primer mensaje, verás en la consola:
```text
[EMBEDDINGS] Cargando modelo local...
[EMBEDDINGS] Modelo listo.
```

---

## 🔑 Obtener API Key de Groq (Gratis)
1. Ve a [console.groq.com](https://console.groq.com).
2. Crea una cuenta gratuita.
3. Ve a **API Keys** → **Create API Key**.
4. Copia tu llave (empieza con `gsk_...`).

## 🐳 Estructura de Docker
- **`web`**: Aplicación Django corriendo con Gunicorn.
- **`db`**: Imagen `ankane/pgvector:latest` (PostgreSQL + Soporte Vectorial).
- **Volúmenes**:
    - `postgres_data`: Persistencia de la base de datos.
    - `hf_cache`: Caché para evitar descargar el modelo de embeddings en cada reinicio.

---

## 📜 Licencia
Este proyecto es de código abierto y gratuito para uso personal y desarrollo.
