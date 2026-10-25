from django.urls import path
from .views import KhoaListAPI, ThongKeLuongKhoaAPI, QuyLuongKhoaAPI

urlpatterns = [

    path('api/khoa/<str:MAKHOA>/thong-ke-luong/', ThongKeLuongKhoaAPI.as_view(), name='thong_ke_luong_khoa'),


    path('api/khoa/<str:MAKHOA>/quy-luong/', QuyLuongKhoaAPI.as_view(), name='quy_luong_khoa'),
    path('api/khoa/', KhoaListAPI.as_view(), name='api_khoa'),
]