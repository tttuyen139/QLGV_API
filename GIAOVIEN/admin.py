from django.contrib import admin

from .models import GiaoVien


@admin.register(GiaoVien)
class GiaoVienAdmin(admin.ModelAdmin):
    list_display = ('ma_gv', 'ho_ten', 'hoc_vi', 'hoc_ham', 'he_so', 'muc_luong', 'ma_khoa')
    list_filter = ('ma_khoa', 'hoc_vi', 'gioi_tinh')
    search_fields = ('ma_gv', 'ho_ten')
