from rest_framework import serializers

from .models import HocVien


class HocVienSerializer(serializers.ModelSerializer):
    ho_ten = serializers.SerializerMethodField()

    class Meta:
        model = HocVien
        fields = ['ma_hv', 'ho', 'ten', 'ho_ten', 'ngay_sinh', 'gioi_tinh', 'noi_sinh', 'ma_lop']

    def get_ho_ten(self, obj):
        return f"{obj.ho} {obj.ten}"
