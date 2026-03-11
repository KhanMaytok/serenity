from django.db import models
from pgvector.django import VectorField


class UserProfile(models.Model):
    """Perfil de usuario con memoria acumulada de Seren."""
    user_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Resumen de patrones detectados por Seren
    pattern_summary = models.TextField(blank=True, default='')
    # Compromisos que el usuario ha hecho
    commitments = models.JSONField(default=list)
    # Metas declaradas
    goals = models.JSONField(default=list)

    def __str__(self):
        return f"User {self.user_id}"

    class Meta:
        db_table = 'user_profiles'


class Memory(models.Model):
    """
    Cada memoria es un fragmento importante de la conversación
    almacenado con su embedding vectorial para búsqueda semántica.
    """
    MEMORY_TYPES = [
        ('commitment', 'Compromiso'),
        ('goal', 'Meta'),
        ('excuse', 'Excusa'),
        ('achievement', 'Logro'),
        ('pattern', 'Patrón'),
        ('context', 'Contexto'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='memories')
    content = models.TextField()
    memory_type = models.CharField(max_length=20, choices=MEMORY_TYPES, default='context')
    embedding = VectorField(dimensions=384)  # text-embedding-3-small
    created_at = models.DateTimeField(auto_now_add=True)
    importance = models.FloatField(default=1.0)  # 1-5, Seren evalúa

    # Si es un compromiso, cuándo se prometió y si se cumplió
    promised_at = models.DateTimeField(null=True, blank=True)
    fulfilled = models.BooleanField(null=True, blank=True)  # None = pendiente

    def __str__(self):
        return f"[{self.memory_type}] {self.content[:60]}..."

    class Meta:
        db_table = 'memories'
        ordering = ['-importance', '-created_at']


class Conversation(models.Model):
    """Historial de conversación por sesión."""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='conversations')
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)  # 'user' o 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['created_at']
