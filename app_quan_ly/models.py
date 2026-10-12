from django.db import models


class Khoa(models.Model):
    ma_khoa = models.CharField(max_length=4, primary_key=True)
    ten_khoa = models.CharField(max_length=40)
    ngay_thanh_lap = models.DateField()
    truong_khoa = models.ForeignKey(
        'GiaoVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='khoa_truong'
    )

    class Meta:
        db_table = 'KHOA'

    def __str__(self):
        return f"{self.ma_khoa} - {self.ten_khoa}"


class GiaoVien(models.Model):
    ma_gv = models.CharField(max_length=4, primary_key=True)
    ho_ten = models.CharField(max_length=40)
    hoc_vi = models.CharField(max_length=10)
    hoc_ham = models.CharField(max_length=10, null=True, blank=True)
    gioi_tinh = models.CharField(max_length=3)
    ngay_sinh = models.DateField()
    ngay_vao_lam = models.DateField()
    he_so = models.DecimalField(max_digits=4, decimal_places=2)
    muc_luong = models.DecimalField(max_digits=15, decimal_places=0)
    ma_khoa = models.ForeignKey(Khoa, on_delete=models.CASCADE, related_name='danh_sach_gv')

    class Meta:
        db_table = 'GIAOVIEN'

    def __str__(self):
        return f"{self.ma_gv} - {self.ho_ten}"


class MonHoc(models.Model):
    ma_mh = models.CharField(max_length=10, primary_key=True)
    ten_mh = models.CharField(max_length=40)
    tin_chi_lt = models.IntegerField()
    tin_chi_th = models.IntegerField()
    ma_khoa = models.ForeignKey(Khoa, on_delete=models.CASCADE, related_name='danh_sach_mon')

    class Meta:
        db_table = 'MONHOC'

    def __str__(self):
        return self.ten_mh


class DieuKien(models.Model):
    ma_mh = models.ForeignKey(MonHoc, on_delete=models.CASCADE, related_name='dieu_kien_mon')
    ma_mh_truoc = models.ForeignKey(MonHoc, on_delete=models.CASCADE, related_name='la_mon_truoc_cua')

    class Meta:
        db_table = 'DIEUKIEN'
        unique_together = ('ma_mh', 'ma_mh_truoc')


class Lop(models.Model):
    ma_lop = models.CharField(max_length=3, primary_key=True)
    ten_lop = models.CharField(max_length=40)
    truong_lop = models.ForeignKey(
        'HocVien', on_delete=models.SET_NULL, null=True, blank=True, related_name='lop_lam_truong'
    )
    si_so = models.IntegerField()
    ma_gvcn = models.ForeignKey(GiaoVien, on_delete=models.CASCADE, related_name='lop_chu_nhiem')

    class Meta:
        db_table = 'LOP'

    def __str__(self):
        return self.ma_lop


class HocVien(models.Model):
    ma_hv = models.CharField(max_length=5, primary_key=True)
    ho = models.CharField(max_length=40)
    ten = models.CharField(max_length=10)
    ngay_sinh = models.DateField()
    gioi_tinh = models.CharField(max_length=3)
    noi_sinh = models.CharField(max_length=40)
    ma_lop = models.ForeignKey(Lop, on_delete=models.CASCADE, related_name='danh_sach_hv')

    class Meta:
        db_table = 'HOCVIEN'

    def __str__(self):
        return f"{self.ho} {self.ten} ({self.ma_hv})"


class GiangDay(models.Model):
    ma_lop = models.ForeignKey(Lop, on_delete=models.CASCADE, related_name='lich_giang_day')
    ma_mh = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
    ma_gv = models.ForeignKey(GiaoVien, on_delete=models.CASCADE)
    hoc_ky = models.IntegerField()
    nam = models.IntegerField()
    tu_ngay = models.DateField()
    den_ngay = models.DateField()

    class Meta:
        db_table = 'GIANGDAY'
        unique_together = ('ma_lop', 'ma_mh')


class KetQuaThi(models.Model):
    ma_hv = models.ForeignKey(HocVien, on_delete=models.CASCADE, related_name='ket_qua_thi')
    ma_mh = models.ForeignKey(MonHoc, on_delete=models.CASCADE)
    lan_thi = models.IntegerField()
    ngay_thi = models.DateField()
    diem = models.DecimalField(max_digits=4, decimal_places=2)
    ket_qua = models.CharField(max_length=10)

    class Meta:
        db_table = 'KETQUATHI'
        unique_together = ('ma_hv', 'ma_mh', 'lan_thi')


from django.db import models

# Create your models here.
