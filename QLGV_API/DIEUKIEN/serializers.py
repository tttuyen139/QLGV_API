from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import DieuKien


class DieuKienSerializer(SQLSerializer):
    class Meta:
        model = DieuKien
        fields = ['MAMH', 'MAMH_TRUOC']
