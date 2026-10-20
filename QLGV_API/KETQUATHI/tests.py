from django.test import TestCase
from rest_framework.test import APIClient

from app_quan_ly.testing import SeedDataMixin
from .services import KetQuaThiService


class KetQuaThiServiceTest(SeedDataMixin, TestCase):
    def test_diem_trung_binh_lay_diem_cao_nhat(self):
        res = KetQuaThiService.tinh_diem_trung_binh_hoc_vien('K1101')
        self.assertEqual(res['so_mon_hoan_thanh'], 4)
        self.assertEqual(res['diem_trung_binh'], 9.38)
        self.assertEqual(res['xep_loai'], "Xuất sắc")

    def test_diem_trung_binh_chua_thi(self):
        res = KetQuaThiService.tinh_diem_trung_binh_hoc_vien('K1312')
        self.assertEqual(res['dtb'], 0)


class KetQuaThiApiTest(SeedDataMixin, TestCase):
    def test_diem_tb_404(self):
        self.assertEqual(APIClient().get('/api/hocvien/XXXXX/DIEM-tb/').status_code, 404)
