from django.contrib import admin
from .models import Phong


# Lịch và đăng ký chỉ ghi qua service để áp dụng khóa và kiểm tra xung đột.
# CRUD phòng cũng dùng API; admin chỉ được xem để không bỏ qua kiểm tra sức chứa.
@admin.register(Phong)
class PhongAdmin(admin.ModelAdmin):
    list_display = ('MAPHONG', 'SUCCHUA', 'LOAI')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
