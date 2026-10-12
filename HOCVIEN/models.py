from django.db import models


class HocVien(models.Model):
    ma_hv = models.CharField(max_length=5, primary_key=True)
    ho = models.CharField(max_length=40)
    ten = models.CharField(max_length=10)
    ngay_sinh = models.DateField()
    gioi_tinh = models.CharField(max_length=3)
    noi_sinh = models.CharField(max_length=40)
    ma_lop = models.ForeignKey('LOP.Lop', on_delete=models.CASCADE, related_name='danh_sach_hv')

    class Meta:
        db_table = 'HOCVIEN'

    def __str__(self):
        return f"{self.ho} {self.ten} ({self.ma_hv})"
