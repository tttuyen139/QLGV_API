from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import GiaoVien


class GiaoVienSerializer(SQLSerializer):
    TENKHOA = serializers.CharField(source='MAKHOA.TENKHOA', read_only=True)
    muc_luong_vnd = serializers.SerializerMethodField()

    def get_muc_luong_vnd(self, obj):
        from app_quan_ly.utils import format_vnd
        return format_vnd(obj.MUCLUONG)

    class Meta:
        model = GiaoVien
        fields = ['MAGV', 'HOTEN', 'HOCVI', 'HOCHAM', 'GIOITINH', 'NGSINH', 'NGVL', 'HESO', 'MUCLUONG', 'MAKHOA', 'muc_luong_vnd', 'TENKHOA']
