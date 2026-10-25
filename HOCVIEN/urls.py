from django.urls import path
from .views import HocVienListAPI

urlpatterns = [
    path('api/hoc-vien/', HocVienListAPI.as_view(), name='hv_list_chuan'),    # URL chuẩn mới
    path('api/hocvien/', HocVienListAPI.as_view(), name='hv_list'),           # Giữ tương thích cũ
]