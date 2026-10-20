from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import KetQuaThi


class KetQuaThiSerializer(SQLSerializer):
    class Meta:
        model = KetQuaThi
        fields = ['MAHV', 'MAMH', 'LANTHI', 'NGTHI', 'DIEM', 'KQUA']
