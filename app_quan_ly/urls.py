from django.urls import path
from .views import ChatBotAPI

urlpatterns = [
    # URL chuẩn chính quy (hết từ "tro-ly-ai")
    path('api/hoc-vu/tu-van-dao-tao/', ChatBotAPI.as_view(), name='tu_van_dao_tao'),

    # Giữ tương thích link cũ
    path('api/ai/tro-ly/', ChatBotAPI.as_view()),
    path('api/tro-ly-ai/', ChatBotAPI.as_view(), name='chatbot_ai'),
]