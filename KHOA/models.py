from django.db import models


class Khoa(models.Model):
    ma_khoa = models.CharField(max_length=4, primary_key=True)
    ten_khoa = models.CharField(max_length=40)
    ngay_thanh_lap = models.DateField()
    truong_khoa = models.ForeignKey(
        'GIAOVIEN.GiaoVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='khoa_truong'
    )

    class Meta:
        db_table = 'KHOA'

    def __str__(self):
        return f"{self.ma_khoa} - {self.ten_khoa}"
