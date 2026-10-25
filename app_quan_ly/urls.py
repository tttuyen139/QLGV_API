from django.urls import path
from .views import ChatBotAPI

urlpatterns = [
    path('api/ai/tro-ly/', ChatBotAPI.as_view(), name='chatbot_ai_chuan'),   # Gom chung vào cụm /api/ai/
    path('api/tro-ly-ai/', ChatBotAPI.as_view(), name='chatbot_ai'),          # Giữ tương thích cũ
]