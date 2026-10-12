from rest_framework import serializers

from app_quan_ly.utils import format_vnd
from .models import GiaoVien


class GiaoVienSerializer(serializers.ModelSerializer):
    muc_luong_vnd = serializers.SerializerMethodField()
    ten_khoa = serializers.CharField(source='ma_khoa.ten_khoa', read_only=True)

    class Meta:
        model = GiaoVien
        fields = ['ma_gv', 'ho_ten', 'hoc_vi', 'hoc_ham', 'gioi_tinh', 'he_so', 'muc_luong', 'muc_luong_vnd', 'ma_khoa', 'ten_khoa']

    def get_muc_luong_vnd(self, obj):
        return format_vnd(obj.muc_luong)
