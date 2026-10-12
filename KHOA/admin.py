from django.contrib import admin

from .models import Khoa


@admin.register(Khoa)
class KhoaAdmin(admin.ModelAdmin):
    list_display = ('ma_khoa', 'ten_khoa', 'ngay_thanh_lap', 'truong_khoa')
    search_fields = ('ma_khoa', 'ten_khoa')
