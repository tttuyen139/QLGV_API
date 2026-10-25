from django.contrib import admin
from django.urls import path, include

from app_quan_ly.student_portal import RoleLoginView, entry, dashboard

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('hoc-vien/', dashboard, name='student-dashboard'),
    path('hoc-vien/dang-xuat/', LogoutView.as_view(next_page='/api-auth/login/'), name='student-logout'),
    path('', entry, name='entry'),
    path('accounts/profile/', entry, name='account-profile'),
    path('api-auth/login/', RoleLoginView.as_view(), name='role-login'),
    path('api/', include('app_quan_ly.student_urls')),
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