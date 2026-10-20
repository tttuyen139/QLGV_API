from datetime import datetime
from decimal import Decimal
from django.db import models
from rest_framework import serializers


class SQLSerializer(serializers.ModelSerializer):
    """Kiểm tra các ràng buộc SQL trước khi ghi; DB vẫn là lớp bảo vệ cuối."""

    def validate(self, attrs):
        data = (
            {f.name: getattr(self.instance, f.name) for f in self.Meta.model._meta.fields if f.name != 'pk'}
            if self.instance
            else {}
        )
        data.update(attrs)
        if self.instance:
            keys = (
                self.Meta.model._meta.pk.field_names
                if self.Meta.model._meta.pk.name == 'pk'
                else [self.Meta.model._meta.pk.name]
            )
            for k in keys:
                if k in attrs and attrs[k] != getattr(self.instance, k):
                    raise serializers.ValidationError('Không được thay đổi khóa chính của bản ghi.')
        errors = {}
        for f in self.Meta.model._meta.fields:
            v = data.get(f.name)
            if v is None:
                continue
            if isinstance(f, models.PositiveSmallIntegerField) and not 0 <= v <= 255:
                errors[f.name] = 'TINYINT phải trong khoảng 0–255.'
            if (
                isinstance(f, models.SmallIntegerField)
                and not isinstance(f, models.PositiveSmallIntegerField)
                and not -32768 <= v <= 32767
            ):
                errors[f.name] = 'SMALLINT ngoài phạm vi.'
            if isinstance(f, models.DateTimeField):
                if not datetime(1900, 1, 1) <= v <= datetime(2079, 6, 6, 23, 59) or v.second or v.microsecond:
                    errors[f.name] = 'SMALLDATETIME: 1900-01-01 đến 2079-06-06, chính xác đến phút.'
        if 'GIOITINH' in data and data['GIOITINH'] not in ('Nam', 'Nữ'):
            errors['GIOITINH'] = 'Chỉ nhận Nam hoặc Nữ.'
        if 'HESO' in data and data['HESO'] <= 0:
            errors['HESO'] = 'Phải > 0.'
        if 'MUCLUONG' in data and not Decimal('0') <= data['MUCLUONG'] <= Decimal('922337203685477.5807'):
            errors['MUCLUONG'] = 'Phải >=0 và trong phạm vi MONEY.'
        if 'NGVL' in data and data['NGVL'] <= data['NGSINH']:
            errors['NGVL'] = 'Phải sau NGSINH.'
        if 'MAMH_TRUOC' in data and data['MAMH_TRUOC'] == data['MAMH']:
            errors['MAMH_TRUOC'] = 'Môn trước phải khác môn hiện tại.'
        if 'HOCKY' in data and not 1 <= data['HOCKY'] <= 3:
            errors['HOCKY'] = 'Phải từ 1 đến 3.'
        if 'TUNGAY' in data and data['TUNGAY'] > data['DENNGAY']:
            errors['DENNGAY'] = 'Phải >= TUNGAY.'
        if 'LANTHI' in data and data['LANTHI'] < 1:
            errors['LANTHI'] = 'Phải >=1.'
        if 'DIEM' in data:
            if not 0 <= data['DIEM'] <= 10:
                errors['DIEM'] = 'Phải từ 0 đến 10.'
            expected = 'Đạt' if data['DIEM'] >= 5 else 'Không đạt'
            if data.get('KQUA') != expected:
                errors['KQUA'] = 'Kết quả phải khớp điểm theo ngưỡng đạt 5.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
