from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import MonHoc


class MonHocSerializer(SQLSerializer):
    class Meta:
        model = MonHoc
        fields = ['MAMH', 'TENMH', 'TCLT', 'TCTH', 'MAKHOA']
