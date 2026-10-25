from django.urls import path
from .views import KiemTraDieuKienAPI, MonTienQuyetAPI

urlpatterns = [
    # Mon tien quyet API
    path('api/hoc-vien/<str:MAHV>/mon-tien-quyet/<str:MAMH>/', MonTienQuyetAPI.as_view(), name='mon_tien_quyet_chuan'),

    # Kiem tra dieu kien API (chuan RESTful & tuong thich cu)
    path('api/hoc-vien/<str:MAHV>/kiem-tra-dieu-kien/<str:MAMH>/', KiemTraDieuKienAPI.as_view(), name='kiem_tra_dk_chuan'),
    path('api/hocvien/<str:MAHV>/kiem-tra-dieu-kien/<str:MAMH>/', KiemTraDieuKienAPI.as_view(), name='kiem_tra_dk'),
]