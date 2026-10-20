from rest_framework import serializers
from app_quan_ly.validation import SQLSerializer
from .models import Lop


class LopSerializer(SQLSerializer):
    class Meta:
        model = Lop
        fields = ['MALOP', 'TENLOP', 'TRGLOP', 'SISO', 'MAGVCN']
