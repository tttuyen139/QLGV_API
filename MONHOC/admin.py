from django.contrib import admin

from .models import MonHoc


@admin.register(MonHoc)
class MonHocAdmin(admin.ModelAdmin):
    list_display = ('MAMH', 'TENMH', 'TCLT', 'TCTH', 'MAKHOA')
    list_filter = ('MAKHOA',)
    search_fields = ('MAMH', 'TENMH')

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
