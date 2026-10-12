from django.contrib import admin

from .models import MonHoc


@admin.register(MonHoc)
class MonHocAdmin(admin.ModelAdmin):
    list_display = ('ma_mh', 'ten_mh', 'tin_chi_lt', 'tin_chi_th', 'ma_khoa')
    list_filter = ('ma_khoa',)
    search_fields = ('ma_mh', 'ten_mh')
