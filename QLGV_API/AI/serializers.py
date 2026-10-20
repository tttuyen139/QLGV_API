from rest_framework import serializers
from .models import Phong, LichHoc


class PhongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phong
        fields = '__all__'

    def validate_SUCCHUA(self, value):
        if value < 1:
            raise serializers.ValidationError('Sức chứa phải lớn hơn 0.')
        if self.instance and self.instance.lichhoc_set.filter(SISO_TOIDA__gt=value).exists():
            raise serializers.ValidationError('Phòng đang có lớp cần nhiều chỗ hơn sức chứa mới.')
        return value


class LichHocSerializer(serializers.ModelSerializer):
    class Meta:
        model = LichHoc
        fields = ['id', 'MALOP', 'MAMH', 'MAPHONG', 'THU', 'CA', 'SISO_TOIDA']
        read_only_fields = fields


class KySerializer(serializers.Serializer):
    HOCKY = serializers.IntegerField(min_value=1, max_value=3)
    NAM = serializers.IntegerField(min_value=1900, max_value=2079)
    luu = serializers.BooleanField(default=False)


class SoThichSerializer(serializers.Serializer):
    tin_chi_min = serializers.IntegerField(min_value=0, max_value=40, default=12)
    tin_chi_max = serializers.IntegerField(min_value=1, max_value=40, default=20)
    thu_tranh = serializers.ListField(child=serializers.IntegerField(min_value=2, max_value=7), default=list)
    ca_uu_tien = serializers.ListField(child=serializers.IntegerField(min_value=1, max_value=4), default=list)
    ma_mon_uu_tien = serializers.ListField(child=serializers.CharField(max_length=10), default=list)

    def validate(self, data):
        if data['tin_chi_min'] > data['tin_chi_max']:
            raise serializers.ValidationError('Tín chỉ tối thiểu phải <= tối đa.')
        return data
