from django.urls import path
from .views import MonTienQuyetAPI, KiemTraDieuKienAPI

urlpatterns = [

    path('api/hoc-vien/<str:MAHV>/mon-tien-quyet/<str:MAMH>/', MonTienQuyetAPI.as_view(), name='mon_tien_quyet_chuan'),


    path('api/hoc-vien/<str:MAHV>/kiem-tra-dieu-kien/<str:MAMH>/', KiemTraDieuKienAPI.as_view()),
    path('api/hocvien/<str:MAHV>/kiem-tra-dieu-kien/<str:MAMH>/', KiemTraDieuKienAPI.as_view(), name='kiem_tra_dk'),
]