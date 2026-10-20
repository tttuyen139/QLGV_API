from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import HocVien


class HocVienSerializer(SQLSerializer):
    class Meta:
        model = HocVien
        fields = ['MAHV', 'HO', 'TEN', 'NGSINH', 'GIOITINH', 'NOISINH', 'MALOP']
