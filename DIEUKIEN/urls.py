from django.urls import path

from .views import KiemTraDieuKienAPI

urlpatterns = [
    path('api/hocvien/<str:ma_hv>/kiem-tra-dieu-kien/<str:ma_mh>/', KiemTraDieuKienAPI.as_view(), name='kiem_tra_dk'),
]
