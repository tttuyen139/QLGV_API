from django.contrib import admin

from .models import Khoa


@admin.register(Khoa)
class KhoaAdmin(admin.ModelAdmin):
    list_display = ('MAKHOA', 'TENKHOA', 'NGTLAP', 'TRGKHOA')
    search_fields = ('MAKHOA', 'TENKHOA')

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
