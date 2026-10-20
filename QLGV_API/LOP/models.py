from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField, SQLTinyIntField


class Lop(models.Model):
    MALOP = SQLCharField(max_length=3, db_column='MALOP', primary_key=True)
    TENLOP = models.CharField(max_length=40, db_column='TENLOP')
    TRGLOP = models.ForeignKey('HOCVIEN.HocVien', on_delete=models.PROTECT, db_column='TRGLOP', null=True, blank=True, related_name='lop_lam_truong')
    SISO = SQLTinyIntField(db_column='SISO')
    MAGVCN = models.ForeignKey('GIAOVIEN.GiaoVien', on_delete=models.PROTECT, db_column='MAGVCN', related_name='lop_chu_nhiem')

    class Meta:
        db_table = 'LOP'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.

    def __str__(self):
        return str(self.pk)
