from django.test import TestCase
from rest_framework.test import APIClient

from app_quan_ly.testing import SeedDataMixin


class HocVienApiTest(SeedDataMixin, TestCase):
    def test_danh_sach(self):
        res = APIClient().get('/api/hocvien/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['total'], 35)
