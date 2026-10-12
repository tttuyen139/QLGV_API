from django.test import TestCase
from rest_framework.test import APIClient

from app_quan_ly.testing import SeedDataMixin
from .services import KhoaService


class KhoaServiceTest(SeedDataMixin, TestCase):
    def test_quy_luong_khoa(self):
        res = KhoaService.tinh_quy_luong_khoa('KHMT')
        self.assertEqual(res['so_luong_giao_vien'], 5)
        self.assertEqual(res['tong_quy_luong'], 8185500)
        self.assertEqual(res['tong_quy_luong_vnd'], "8.185.500 VNĐ")

    def test_quy_luong_khoa_khong_ton_tai(self):
        self.assertIsNone(KhoaService.tinh_quy_luong_khoa('XXXX'))


class KhoaApiTest(SeedDataMixin, TestCase):
    def test_quy_luong_404(self):
        res = APIClient().get('/api/khoa/XXXX/quy-luong/')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['status'], 'error')
