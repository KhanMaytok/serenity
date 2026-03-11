from django.urls import path
from chat import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/chat/', views.chat, name='chat'),
    path('api/memories/<str:user_id>/', views.get_memories, name='get_memories'),
    path('api/memories/<str:user_id>/clear/', views.clear_memories, name='clear_memories'),
]
