from django.db import models
from app_quan_ly.fields import SQLCharField, SQLVarCharField, SmallDateTimeField, MoneyField, SQLTinyIntField


class KetQuaThi(models.Model):
    pk = models.CompositePrimaryKey('MAHV', 'MAMH', 'LANTHI')
    MAHV = models.ForeignKey('HOCVIEN.HocVien', on_delete=models.PROTECT, db_column='MAHV', related_name='ket_qua_thi')
    MAMH = models.ForeignKey('MONHOC.MonHoc', on_delete=models.PROTECT, db_column='MAMH')
    LANTHI = SQLTinyIntField(db_column='LANTHI')
    NGTHI = SmallDateTimeField(db_column='NGTHI')
    DIEM = models.DecimalField(max_digits=4, decimal_places=2, db_column='DIEM')
    KQUA = models.CharField(max_length=10, db_column='KQUA')

    class Meta:
        db_table = 'KETQUATHI'
        managed = False  # SQL chuẩn sở hữu DDL; Django không ALTER 8 bảng BRD.

    def __str__(self):
        return str(self.pk)
