from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField, SQLTinyIntField


class GiangDay(models.Model):
    pk = models.CompositePrimaryKey('MALOP', 'MAMH')
    MALOP = models.ForeignKey('LOP.Lop', on_delete=models.PROTECT, db_column='MALOP', related_name='lich_giang_day')
    MAMH = models.ForeignKey('MONHOC.MonHoc', on_delete=models.PROTECT, db_column='MAMH')
    MAGV = models.ForeignKey('GIAOVIEN.GiaoVien', on_delete=models.PROTECT, db_column='MAGV')
    HOCKY = SQLTinyIntField(db_column='HOCKY')
    NAM = models.SmallIntegerField(db_column='NAM')
    TUNGAY = SmallDateTimeField(db_column='TUNGAY')
    DENNGAY = SmallDateTimeField(db_column='DENNGAY')

    class Meta:
        db_table = 'GIANGDAY'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.

    def __str__(self):
        return str(self.pk)
