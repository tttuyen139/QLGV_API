from django.db import models


class GiangDay(models.Model):
    ma_lop = models.ForeignKey('LOP.Lop', on_delete=models.CASCADE, related_name='lich_giang_day')
    ma_mh = models.ForeignKey('MONHOC.MonHoc', on_delete=models.CASCADE)
    ma_gv = models.ForeignKey('GIAOVIEN.GiaoVien', on_delete=models.CASCADE)
    hoc_ky = models.IntegerField()
    nam = models.IntegerField()
    tu_ngay = models.DateField()
    den_ngay = models.DateField()

    class Meta:
        db_table = 'GIANGDAY'
        unique_together = ('ma_lop', 'ma_mh')
