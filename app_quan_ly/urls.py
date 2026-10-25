from django.urls import path
from .views import ChatBotAPI

urlpatterns = [
    # URL chuẩn chính quy cho tư vấn đào tạo học vụ
    path('api/hoc-vu/tu-van-dao-tao/', ChatBotAPI.as_view(), name='tu_van_dao_tao'),

    # Các đường dẫn tương thích cũ / AI trợ lý
    path('api/ai/tro-ly/', ChatBotAPI.as_view(), name='chatbot_ai_chuan'),
    path('api/tro-ly-ai/', ChatBotAPI.as_view(), name='chatbot_ai'),
]