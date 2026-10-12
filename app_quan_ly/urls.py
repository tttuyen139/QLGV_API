from django.urls import path

from .views import ChatBotAPI

urlpatterns = [
    # Trợ lý ảo AI
    path('api/tro-ly-ai/', ChatBotAPI.as_view(), name='chatbot_ai'),
]
