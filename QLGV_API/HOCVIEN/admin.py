from django.contrib import admin

from .models import HocVien


@admin.register(HocVien)
class HocVienAdmin(admin.ModelAdmin):
    list_display = ('MAHV', 'HO', 'TEN', 'NGSINH', 'GIOITINH', 'NOISINH', 'MALOP')
    list_filter = ('MALOP', 'GIOITINH')
    search_fields = ('MAHV', 'HO', 'TEN')

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
