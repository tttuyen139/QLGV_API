from django.urls import path

from .views import QuyLuongKhoaAPI

urlpatterns = [
    path('api/khoa/<str:ma_khoa>/quy-luong/', QuyLuongKhoaAPI.as_view(), name='quy_luong'),
]
