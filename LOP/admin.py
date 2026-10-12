from django.contrib import admin

from .models import Lop


@admin.register(Lop)
class LopAdmin(admin.ModelAdmin):
    list_display = ('ma_lop', 'ten_lop', 'si_so', 'truong_lop', 'ma_gvcn')
