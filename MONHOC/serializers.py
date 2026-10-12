from rest_framework import serializers

from .models import MonHoc


class MonHocSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = '__all__'
