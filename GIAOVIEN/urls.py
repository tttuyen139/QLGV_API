from django.urls import path
from .views import GiaoVienListAPI

urlpatterns = [
    path('api/giao-vien/', GiaoVienListAPI.as_view(), name='gv_list_chuan'),  # URL chuẩn mới
    path('api/giaovien/', GiaoVienListAPI.as_view(), name='gv_list'),         # Giữ tương thích cũ
]