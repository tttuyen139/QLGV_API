from django.db import models


class Phong(models.Model):
    MAPHONG = models.CharField(max_length=10, primary_key=True)
    SUCCHUA = models.PositiveSmallIntegerField()
    LOAI = models.CharField(max_length=2, choices=[('LT', 'Lý thuyết'), ('TH', 'Thực hành')], default='LT')

    class Meta:
        db_table = 'PHONG'
        constraints = [models.CheckConstraint(condition=models.Q(SUCCHUA__gt=0), name='CK_PHONG_SUCCHUA')]

    def __str__(self):
        return self.MAPHONG


class LichHoc(models.Model):
    # Tham chiếu từng mã; cặp MALOP/MAMH phải tồn tại trong GIANGDAY (service kiểm tra).
    MALOP = models.ForeignKey('LOP.Lop', db_column='MALOP', on_delete=models.PROTECT)
    MAMH = models.ForeignKey('MONHOC.MonHoc', db_column='MAMH', on_delete=models.PROTECT)
    MAPHONG = models.ForeignKey(Phong, db_column='MAPHONG', on_delete=models.PROTECT)
    THU = models.PositiveSmallIntegerField()
    CA = models.PositiveSmallIntegerField()
    SISO_TOIDA = models.PositiveSmallIntegerField()
    # Chỉ service xác nhận được ghi; không mở CRUD JSON từ client.
    DANGKY = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'LICHHOC'
        constraints = [
            models.UniqueConstraint(fields=['MALOP', 'MAMH'], name='UQ_LICHHOC_GIANGDAY'),
            models.CheckConstraint(condition=models.Q(THU__gte=2, THU__lte=7), name='CK_LICHHOC_THU'),
            models.CheckConstraint(condition=models.Q(CA__gte=1, CA__lte=4), name='CK_LICHHOC_CA'),
            models.CheckConstraint(condition=models.Q(SISO_TOIDA__gt=0), name='CK_LICHHOC_SISO'),
        ]
