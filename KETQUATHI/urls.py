from django.urls import path
from .views import DiemTrungBinhHocVienAPI

urlpatterns = [
    # URL chuẩn mới: hết viết hoa, rõ nghĩa "diem-trung-binh"
    path('api/hoc-vien/<str:MAHV>/diem-trung-binh/', DiemTrungBinhHocVienAPI.as_view(), name='dtb_hv_chuan'),
    # Giữ tương thích cũ
    path('api/hocvien/<str:MAHV>/diem-tb/', DiemTrungBinhHocVienAPI.as_view()),
    path('api/hocvien/<str:MAHV>/DIEM-tb/', DiemTrungBinhHocVienAPI.as_view(), name='dtb_hv'),
]