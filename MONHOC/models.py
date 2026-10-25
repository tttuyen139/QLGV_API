from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField, SQLTinyIntField


class MonHoc(models.Model):
    MAMH = SQLVarCharField(max_length=10, db_column='MAMH', primary_key=True)
    TENMH = models.CharField(max_length=40, db_column='TENMH')
    TCLT = SQLTinyIntField(db_column='TCLT')
    TCTH = SQLTinyIntField(db_column='TCTH')
    MAKHOA = models.ForeignKey('KHOA.Khoa', on_delete=models.PROTECT, db_column='MAKHOA', related_name='danh_sach_mon')

    class Meta:
        db_table = 'MONHOC'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.
        verbose_name = 'Môn học'
        verbose_name_plural = 'Danh sách môn học'

    def __str__(self):
        return str(self.pk)