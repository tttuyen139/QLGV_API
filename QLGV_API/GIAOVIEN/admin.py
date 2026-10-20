from django.contrib import admin

from .models import GiaoVien


@admin.register(GiaoVien)
class GiaoVienAdmin(admin.ModelAdmin):
    list_display = ('MAGV', 'HOTEN', 'HOCVI', 'HOCHAM', 'HESO', 'MUCLUONG', 'MAKHOA')
    list_filter = ('MAKHOA', 'HOCVI', 'GIOITINH')
    search_fields = ('MAGV', 'HOTEN')

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
