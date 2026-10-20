from django.test import TestCase
from rest_framework.test import APIClient

from app_quan_ly.testing import SeedDataMixin
from .services import DieuKienService


class DieuKienServiceTest(SeedDataMixin, TestCase):
    def test_dieu_kien_du(self):
        res = DieuKienService.kiem_tra_dieu_kien_hoc_mon('K1101', 'CSDL')
        self.assertTrue(res['du_dieu_kien'])

    def test_dieu_kien_thieu_mon_truoc(self):
        res = DieuKienService.kiem_tra_dieu_kien_hoc_mon('K1102', 'PTTKHTTT')
        self.assertFalse(res['du_dieu_kien'])
        self.assertEqual(res['mon_chua_dat'], 'CSDL')

    def test_mon_khong_co_dieu_kien(self):
        res = DieuKienService.kiem_tra_dieu_kien_hoc_mon('K1101', 'THDC')
        self.assertTrue(res['du_dieu_kien'])


class DieuKienApiTest(SeedDataMixin, TestCase):
    def test_kiem_tra_dieu_kien(self):
        res = APIClient().get('/api/hocvien/K1101/kiem-tra-dieu-kien/CSDL/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['KQUA']['du_dieu_kien'])
