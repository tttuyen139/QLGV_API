from django.db import models


class DieuKien(models.Model):
    ma_mh = models.ForeignKey('MONHOC.MonHoc', on_delete=models.CASCADE, related_name='dieu_kien_mon')
    ma_mh_truoc = models.ForeignKey('MONHOC.MonHoc', on_delete=models.CASCADE, related_name='la_mon_truoc_cua')

    class Meta:
        db_table = 'DIEUKIEN'
        unique_together = ('ma_mh', 'ma_mh_truoc')
