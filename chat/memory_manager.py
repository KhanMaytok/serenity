"""
memory_manager.py
Memoria de huechina con embeddings locales (sentence-transformers) — sin API, 100% gratis.
El modelo se descarga automáticamente la primera vez (~90MB).
Modelo elegido: paraphrase-multilingual-MiniLM-L12-v2
  → optimizado para español, rápido, 384 dimensiones.
"""
import json
from datetime import datetime
from django.conf import settings
from pgvector.django import CosineDistance

# Singleton: cargamos el modelo una sola vez en memoria
_embedding_model = None


def get_embedding_model():
    """Carga el modelo de embeddings localmente (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[EMBEDDINGS] Cargando modelo local: {settings.EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("[EMBEDDINGS] Modelo listo.")
    return _embedding_model


def get_embedding(text: str) -> list[float]:
    """Genera embedding vectorial localmente, sin llamadas a API."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def search_relevant_memories(user, query: str, limit: int = None) -> list:
    """Búsqueda semántica con pgvector."""
    from chat.models import Memory
    if limit is None:
        limit = settings.MEMORY_RESULTS

    query_embedding = get_embedding(query)

    memories = (
        Memory.objects
        .filter(user=user)
        .annotate(distance=CosineDistance('embedding', query_embedding))
        .order_by('distance')[:limit]
    )
    return list(memories)


def extract_and_store_memories(user, user_message: str, assistant_response: str):
    """
    Usa Groq/Llama para extraer memorias importantes y las guarda con embeddings locales.
    """
    from chat.models import Memory
    from groq import Groq

    groq_client = Groq(api_key=settings.GROQ_API_KEY)

    extraction_prompt = f"""Analiza este intercambio y extrae SOLO información que valga la pena recordar a largo plazo.

Usuario dijo: "{user_message}"
huechina respondió: "{assistant_response}"

Devuelve ÚNICAMENTE un objeto JSON válido, sin markdown, sin texto adicional:
{{
  "memories": [
    {{
      "content": "descripción concisa del recuerdo",
      "type": "commitment|goal|excuse|achievement|pattern|context",
      "importance": 1,
      "is_commitment": false
    }}
  ]
}}

Reglas:
- Solo extrae si hay información valiosa (compromiso, meta, patrón, logro, excusa recurrente)
- Si no hay nada importante, devuelve: {{"memories": []}}
- importance va de 1 a 5 (5 = compromiso explícito o meta crítica)
- is_commitment = true solo si el usuario prometió hacer algo concreto"""

    response = groq_client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": extraction_prompt}],
        temperature=0.1,
        max_tokens=500,
    )

    try:
        raw = response.choices[0].message.content.strip()
        raw = raw.replace('```json', '').replace('```', '').strip()
        data = json.loads(raw)
        memories_data = data.get('memories', [])
    except (json.JSONDecodeError, KeyError, AttributeError):
        return

    for mem_data in memories_data:
        if not mem_data.get('content'):
            continue

        embedding = get_embedding(mem_data['content'])

        memory = Memory(
            user=user,
            content=mem_data['content'],
            memory_type=mem_data.get('type', 'context'),
            embedding=embedding,
            importance=float(mem_data.get('importance', 1.0)),
        )

        if mem_data.get('is_commitment'):
            memory.promised_at = datetime.now()

        memory.save()


def build_memory_context(user, current_message: str) -> str:
    """Construye el bloque de memoria que se inyecta en el system prompt."""
    memories = search_relevant_memories(user, current_message)

    if not memories:
        return ""

    commitments = [m for m in memories if m.memory_type == 'commitment' and m.fulfilled is None]
    patterns = [m for m in memories if m.memory_type in ('pattern', 'excuse')]
    other = [m for m in memories if m.memory_type not in ('commitment', 'pattern', 'excuse')]

    lines = ["=== MEMORIA DE huechina ==="]

    if commitments:
        lines.append("\nCOMPROMISOS PENDIENTES DEL USUARIO:")
        for m in commitments:
            date_str = m.promised_at.strftime('%d/%m/%Y') if m.promised_at else 'fecha desconocida'
            lines.append(f"  • [{date_str}] {m.content}")

    if patterns:
        lines.append("\nPATRONES Y EXCUSAS DETECTADOS:")
        for m in patterns:
            lines.append(f"  • {m.content}")

    if other:
        lines.append("\nCONTEXTO RELEVANTE:")
        for m in other:
            lines.append(f"  • {m.content}")

    lines.append("\n=== FIN MEMORIA ===")
    lines.append("Usa esta memoria para confrontar inconsistencias y dar seguimiento.")

    return "\n".join(lines)
