from django.urls import path

from .views import KiemTraDieuKienAPI

urlpatterns = [
    path('api/hocvien/<str:MAHV>/kiem-tra-dieu-kien/<str:MAMH>/', KiemTraDieuKienAPI.as_view(), name='kiem_tra_dk'),
]
