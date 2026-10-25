from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField


class HocVien(models.Model):
    MAHV = SQLCharField(max_length=5, db_column='MAHV', primary_key=True)
    HO = models.CharField(max_length=40, db_column='HO')
    TEN = models.CharField(max_length=10, db_column='TEN')
    NGSINH = SmallDateTimeField(db_column='NGSINH')
    GIOITINH = models.CharField(max_length=3, db_column='GIOITINH')
    NOISINH = models.CharField(max_length=40, db_column='NOISINH')
    MALOP = models.ForeignKey('LOP.Lop', on_delete=models.PROTECT, db_column='MALOP', related_name='danh_sach_hv')

    class Meta:
        db_table = 'HOCVIEN'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.
        verbose_name = 'Học viên'
        verbose_name_plural = 'Danh sách học viên'

    def __str__(self):
        return str(self.pk)