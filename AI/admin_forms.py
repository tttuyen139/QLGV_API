from django import forms
from rest_framework.exceptions import ValidationError as APIValidationError

from GIANGDAY.models import GiangDay
from .models import Phong
from .serializers import PhongSerializer


class XepLichForm(forms.Form):
    HOCKY = forms.TypedChoiceField(label='Học kỳ', choices=[(1, 'Học kỳ 1'), (2, 'Học kỳ 2'), (3, 'Học kỳ 3')], coerce=int)
    NAM = forms.TypedChoiceField(label='Năm', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        years = list(GiangDay.objects.order_by('-NAM').values_list('NAM', flat=True).distinct())
        self.fields['NAM'].choices = [(year, year) for year in years]
        if years:
            self.fields['NAM'].initial = years[0]


class PhongAdminForm(forms.ModelForm):
    class Meta:
        model = Phong
        fields = ['MAPHONG', 'SUCCHUA', 'LOAI']
        labels = {'MAPHONG': 'Mã phòng', 'SUCCHUA': 'Sức chứa', 'LOAI': 'Loại phòng'}

    def clean(self):
        data = super().clean()
        if self.errors:
            return data
        instance = Phong.objects.filter(pk=self.instance.pk).first() if self.instance.pk else None
        payload = {**data, 'MAPHONG': instance.pk} if instance else data
        validator = PhongSerializer(instance, data=payload)
        try:
            validator.is_valid(raise_exception=True)
        except APIValidationError as exc:
            for name, errors in exc.detail.items():
                self.add_error(name if name in self.fields else None, ' '.join(map(str, errors)))
        return data
