from django.urls import path
from .views import MonHocListAPI

urlpatterns = [
    path('api/mon-hoc/', MonHocListAPI.as_view(), name='mh_list_chuan'),     # URL chuẩn mới
    path('api/monhoc/', MonHocListAPI.as_view(), name='mh_list'),            # Giữ tương thích cũ
]