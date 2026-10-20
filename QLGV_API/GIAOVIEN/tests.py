from django.test import TestCase
from rest_framework.test import APIClient

from app_quan_ly.testing import SeedDataMixin


class GiaoVienApiTest(SeedDataMixin, TestCase):
    def test_danh_sach(self):
        res = APIClient().get('/api/giaovien/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['total'], 15)

    def test_giaovien_co_luong_vnd(self):
        data = APIClient().get('/api/giaovien/').json()['data']
        gv01 = next(gv for gv in data if gv['MAGV'] == 'GV01')
        self.assertEqual(gv01['muc_luong_vnd'], "2.250.000 VNĐ")
        self.assertEqual(gv01['TENKHOA'], "Khoa học máy tính")
