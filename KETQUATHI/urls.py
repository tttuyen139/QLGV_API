from django.urls import path

from .views import DiemTrungBinhHocVienAPI

urlpatterns = [
    path('api/hocvien/<str:ma_hv>/diem-tb/', DiemTrungBinhHocVienAPI.as_view(), name='dtb_hv'),
]
