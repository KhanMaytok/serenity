# Seren — Groq + Embeddings Locales (100% Gratuito)

Stack completamente gratuito:
- **Chat**: Groq API — llama-3.3-70b-versatile (gratis)
- **Embeddings**: sentence-transformers local — sin API (gratis)
- **Base de datos**: PostgreSQL + pgvector

## Setup en 5 pasos

### 1. PostgreSQL + pgvector

```bash
sudo apt install postgresql-16-pgvector
psql -U postgres -c "CREATE DATABASE seren_db;"
```

### 2. API Key de Groq (gratis)

1. Ve a https://console.groq.com
2. Crea cuenta → API Keys → Create API Key
3. Copia la key (empieza con `gsk_...`)

### 3. Variables de entorno

```bash
cp .env.example .env
# Pega tu GROQ_API_KEY en el .env
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
# Nota: torch + sentence-transformers pesan ~1.5GB
# El modelo de embeddings (~90MB) se descarga automáticamente al primer uso
```

### 5. Migrar y correr

```bash
python manage.py migrate
python manage.py runserver
```

Abre → http://localhost:8000

## Primera vez que corre

Al enviar el primer mensaje, verás en consola:

```
[EMBEDDINGS] Cargando modelo local: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
[EMBEDDINGS] Modelo listo.
```

Esto ocurre una sola vez por sesión del servidor. Después es instantáneo.

## Por qué este modelo de embeddings

`paraphrase-multilingual-MiniLM-L12-v2`:
- ✅ Optimizado para español
- ✅ 384 dimensiones (ligero y rápido)
- ✅ Corre en CPU sin problema
- ✅ ~90MB descarga única

## Límites gratuitos de Groq

| Modelo | Requests/min | Tokens/min | Tokens/día |
|--------|-------------|------------|------------|
| llama-3.3-70b | 30 | 6,000 | 100,000 |

Suficiente para desarrollo y pruebas extensas.
