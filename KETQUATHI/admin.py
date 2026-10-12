from django.contrib import admin

from .models import KetQuaThi


@admin.register(KetQuaThi)
class KetQuaThiAdmin(admin.ModelAdmin):
    list_display = ('ma_hv', 'ma_mh', 'lan_thi', 'ngay_thi', 'diem', 'ket_qua')
    list_filter = ('ma_mh', 'ket_qua')
    search_fields = ('ma_hv__ma_hv',)
