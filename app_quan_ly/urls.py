from django.urls import path
from .views import (
    GiaoVienListAPI,
    HocVienListAPI,
    MonHocListAPI,
    QuyLuongKhoaAPI,
    DiemTrungBinhHocVienAPI,
    KiemTraDieuKienAPI,
    ChatBotAPI  # API Trợ lý ảo AI
)

urlpatterns = [
    # Danh mục
    path('api/giaovien/', GiaoVienListAPI.as_view(), name='gv_list'),
    path('api/hocvien/', HocVienListAPI.as_view(), name='hv_list'),
    path('api/monhoc/', MonHocListAPI.as_view(), name='mh_list'),

    # cv tầng Service
    path('api/khoa/<str:ma_khoa>/quy-luong/', QuyLuongKhoaAPI.as_view(), name='quy_luong'),
    path('api/hocvien/<str:ma_hv>/diem-tb/', DiemTrungBinhHocVienAPI.as_view(), name='dtb_hv'),
    path('api/hocvien/<str:ma_hv>/kiem-tra-dieu-kien/<str:ma_mh>/', KiemTraDieuKienAPI.as_view(), name='kiem_tra_dk'),

    # Trợ lý ảo AI
    path('api/tro-ly-ai/', ChatBotAPI.as_view(), name='chatbot_ai'),
]