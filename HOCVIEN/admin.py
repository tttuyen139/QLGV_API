from django.contrib import admin

from .models import HocVien


@admin.register(HocVien)
class HocVienAdmin(admin.ModelAdmin):
    list_display = ('ma_hv', 'ho', 'ten', 'ngay_sinh', 'gioi_tinh', 'noi_sinh', 'ma_lop')
    list_filter = ('ma_lop', 'gioi_tinh')
    search_fields = ('ma_hv', 'ho', 'ten')
