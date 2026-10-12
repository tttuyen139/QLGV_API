from django.db import models


class MonHoc(models.Model):
    ma_mh = models.CharField(max_length=10, primary_key=True)
    ten_mh = models.CharField(max_length=40)
    tin_chi_lt = models.IntegerField()
    tin_chi_th = models.IntegerField()
    ma_khoa = models.ForeignKey('KHOA.Khoa', on_delete=models.CASCADE, related_name='danh_sach_mon')

    class Meta:
        db_table = 'MONHOC'

    def __str__(self):
        return self.ten_mh
