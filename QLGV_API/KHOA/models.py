from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField


class Khoa(models.Model):
    MAKHOA = SQLVarCharField(max_length=4, db_column='MAKHOA', primary_key=True)
    TENKHOA = models.CharField(max_length=40, db_column='TENKHOA')
    NGTLAP = SmallDateTimeField(db_column='NGTLAP')
    TRGKHOA = models.ForeignKey('GIAOVIEN.GiaoVien', on_delete=models.PROTECT, db_column='TRGKHOA', null=True, blank=True, related_name='khoa_truong')

    class Meta:
        db_table = 'KHOA'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.

    def __str__(self):
        return str(self.pk)
