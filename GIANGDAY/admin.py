from django.contrib import admin

from .models import GiangDay


@admin.register(GiangDay)
class GiangDayAdmin(admin.ModelAdmin):
    list_display = ('ma_lop', 'ma_mh', 'ma_gv', 'hoc_ky', 'nam', 'tu_ngay', 'den_ngay')
    list_filter = ('nam', 'hoc_ky', 'ma_lop')
