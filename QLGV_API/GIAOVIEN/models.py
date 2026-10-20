from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField


class GiaoVien(models.Model):
    MAGV = SQLCharField(max_length=4, db_column='MAGV', primary_key=True)
    HOTEN = models.CharField(max_length=40, db_column='HOTEN')
    HOCVI = models.CharField(max_length=10, db_column='HOCVI')
    HOCHAM = models.CharField(max_length=10, db_column='HOCHAM', null=True, blank=True)
    GIOITINH = models.CharField(max_length=3, db_column='GIOITINH')
    NGSINH = SmallDateTimeField(db_column='NGSINH')
    NGVL = SmallDateTimeField(db_column='NGVL')
    HESO = models.DecimalField(max_digits=4, decimal_places=2, db_column='HESO')
    MUCLUONG = MoneyField(db_column='MUCLUONG')
    MAKHOA = models.ForeignKey('KHOA.Khoa', on_delete=models.PROTECT, db_column='MAKHOA', related_name='danh_sach_gv')

    class Meta:
        db_table = 'GIAOVIEN'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.

    def __str__(self):
        return str(self.pk)
