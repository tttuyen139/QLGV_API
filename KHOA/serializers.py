from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import Khoa


class KhoaSerializer(SQLSerializer):
    class Meta:
        model = Khoa
        fields = ['MAKHOA', 'TENKHOA', 'NGTLAP', 'TRGKHOA']
