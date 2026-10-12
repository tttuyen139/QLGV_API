from django.db import models


class KetQuaThi(models.Model):
    ma_hv = models.ForeignKey('HOCVIEN.HocVien', on_delete=models.CASCADE, related_name='ket_qua_thi')
    ma_mh = models.ForeignKey('MONHOC.MonHoc', on_delete=models.CASCADE)
    lan_thi = models.IntegerField()
    ngay_thi = models.DateField()
    diem = models.DecimalField(max_digits=4, decimal_places=2)
    ket_qua = models.CharField(max_length=10)

    class Meta:
        db_table = 'KETQUATHI'
        unique_together = ('ma_hv', 'ma_mh', 'lan_thi')
