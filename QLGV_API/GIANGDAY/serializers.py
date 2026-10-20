from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import GiangDay


class GiangDaySerializer(SQLSerializer):
    class Meta:
        model = GiangDay
        fields = ['MALOP', 'MAMH', 'MAGV', 'HOCKY', 'NAM', 'TUNGAY', 'DENNGAY']
