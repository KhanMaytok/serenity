import json
import uuid
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from chat.models import UserProfile, Conversation
from chat.memory_manager import build_memory_context, extract_and_store_memories
from chat.seren_engine import chat_with_seren


def index(request):
    """Sirve el frontend."""
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """
    Endpoint principal de chat con Seren.
    
    Body JSON:
    {
        "user_id": "string (opcional, se genera si no existe)",
        "session_id": "string (opcional)",
        "message": "string"
    }
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    user_message = body.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)

    user_id = body.get("user_id") or str(uuid.uuid4())
    session_id = body.get("session_id") or str(uuid.uuid4())

    # Obtener o crear perfil de usuario
    user, created = UserProfile.objects.get_or_create(user_id=user_id)

    # Recuperar historial de la sesión (últimos 20 mensajes)
    session_history = Conversation.objects.filter(
        user=user,
        session_id=session_id
    ).order_by('-created_at')[:20]

    messages_history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(session_history)
    ]

    # Construir contexto de memoria semántica
    memory_context = ""
    try:
        memory_context = build_memory_context(user, user_message)
    except Exception as e:
        # Si pgvector falla (ej: sin configurar), continúa sin memoria
        print(f"[MEMORIA] Error: {e}")

    # Agregar mensaje actual al historial
    messages_history.append({"role": "user", "content": user_message})

    # Respuesta de Seren
    try:
        assistant_response = chat_with_seren(messages_history, memory_context)
    except Exception as e:
        return JsonResponse({"error": f"Error con OpenAI: {str(e)}"}, status=500)

    # Guardar en historial
    Conversation.objects.create(
        user=user,
        session_id=session_id,
        role="user",
        content=user_message
    )
    Conversation.objects.create(
        user=user,
        session_id=session_id,
        role="assistant",
        content=assistant_response
    )

    # Extraer y guardar memorias en background (async si tienes Celery, sync aquí)
    try:
        extract_and_store_memories(user, user_message, assistant_response)
    except Exception as e:
        print(f"[MEMORIA] Error extrayendo memorias: {e}")

    return JsonResponse({
        "response": assistant_response,
        "user_id": user_id,
        "session_id": session_id,
        "memory_used": bool(memory_context),
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_memories(request, user_id):
    """Devuelve las memorias de un usuario (para debug/panel)."""
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    memories = user.memories.all().values(
        'id', 'content', 'memory_type', 'importance',
        'created_at', 'promised_at', 'fulfilled'
    )

    return JsonResponse({
        "user_id": user_id,
        "memories": list(memories),
        "total": len(list(memories))
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def clear_memories(request, user_id):
    """Limpia memorias de un usuario."""
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    count, _ = user.memories.all().delete()
    return JsonResponse({"deleted": count})
