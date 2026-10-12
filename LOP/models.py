from django.db import models


class Lop(models.Model):
    ma_lop = models.CharField(max_length=3, primary_key=True)
    ten_lop = models.CharField(max_length=40)
    truong_lop = models.ForeignKey(
        'HOCVIEN.HocVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='lop_lam_truong'
    )
    si_so = models.IntegerField()
    ma_gvcn = models.ForeignKey('GIAOVIEN.GiaoVien', on_delete=models.CASCADE, related_name='lop_chu_nhiem')

    class Meta:
        db_table = 'LOP'

    def __str__(self):
        return self.ma_lop
