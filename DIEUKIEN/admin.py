from django.contrib import admin

from .models import DieuKien


@admin.register(DieuKien)
class DieuKienAdmin(admin.ModelAdmin):
    list_display = ('ma_mh', 'ma_mh_truoc')
