from django.db import models


class GiaoVien(models.Model):
    ma_gv = models.CharField(max_length=4, primary_key=True)
    ho_ten = models.CharField(max_length=40)
    hoc_vi = models.CharField(max_length=10)
    hoc_ham = models.CharField(max_length=10, null=True, blank=True)
    gioi_tinh = models.CharField(max_length=3)
    ngay_sinh = models.DateField()
    ngay_vao_lam = models.DateField()
    he_so = models.DecimalField(max_digits=4, decimal_places=2)
    muc_luong = models.DecimalField(max_digits=15, decimal_places=0)
    ma_khoa = models.ForeignKey('KHOA.Khoa', on_delete=models.CASCADE, related_name='danh_sach_gv')

    class Meta:
        db_table = 'GIAOVIEN'

    def __str__(self):
        return f"{self.ma_gv} - {self.ho_ten}"
