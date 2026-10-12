from rest_framework import serializers
from .models import GiaoVien, HocVien, MonHoc

class GiaoVienSerializer(serializers.ModelSerializer):
    muc_luong_vnd = serializers.SerializerMethodField()
    ten_khoa = serializers.CharField(source='ma_khoa.ten_khoa', read_only=True)

    class Meta:
        model = GiaoVien
        fields = ['ma_gv', 'ho_ten', 'hoc_vi', 'hoc_ham', 'gioi_tinh', 'he_so', 'muc_luong', 'muc_luong_vnd', 'ma_khoa', 'ten_khoa']

    def get_muc_luong_vnd(self, obj):
        return f"{int(obj.muc_luong):,} VNĐ".replace(',', '.')

class HocVienSerializer(serializers.ModelSerializer):
    ho_ten = serializers.SerializerMethodField()

    class Meta:
        model = HocVien
        fields = ['ma_hv', 'ho', 'ten', 'ho_ten', 'ngay_sinh', 'gioi_tinh', 'noi_sinh', 'ma_lop']

    def get_ho_ten(self, obj):
        return f"{obj.ho} {obj.ten}"

class MonHocSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = '__all__'