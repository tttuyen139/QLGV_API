from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('AI.urls')),
    path('', include('app_quan_ly.core_urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('', include('KHOA.urls')),
    path('', include('GIAOVIEN.urls')),
    path('', include('MONHOC.urls')),
    path('', include('DIEUKIEN.urls')),
    path('', include('HOCVIEN.urls')),
    path('', include('KETQUATHI.urls')),
    path('', include('app_quan_ly.urls')),
]

# Tùy chỉnh tiêu đề trang Quản trị Admin cho chuyên nghiệp (xóa chữ "Site quản trị hệ thống.")
admin.site.site_header = "HỆ THỐNG QUẢN LÝ GIÁO VỤ"
admin.site.site_title = "Quản Lý Giáo Vụ"
admin.site.index_title = "Bảng Điều Khiển Quản Trị Hệ Thống"