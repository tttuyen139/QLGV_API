from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField


class DieuKien(models.Model):
    pk = models.CompositePrimaryKey('MAMH', 'MAMH_TRUOC')
    MAMH = models.ForeignKey('MONHOC.MonHoc', on_delete=models.PROTECT, db_column='MAMH', related_name='dieu_kien_mon')
    MAMH_TRUOC = models.ForeignKey('MONHOC.MonHoc', on_delete=models.PROTECT, db_column='MAMH_TRUOC', related_name='la_mon_truoc_cua')

    class Meta:
        db_table = 'DIEUKIEN'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.

    def __str__(self):
        return str(self.pk)
