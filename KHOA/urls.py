from django.urls import path

from .views import KhoaListAPI, QuyLuongKhoaAPI

urlpatterns = [
    path('api/khoa/<str:MAKHOA>/quy-luong/', QuyLuongKhoaAPI.as_view(), name='quy_luong_khoa'),
    path('api/khoa/', KhoaListAPI.as_view(), name='api_khoa'),
]
