from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .utils import format_vnd


class FormatVndTest(TestCase):
    def test_format(self):
        self.assertEqual(format_vnd(2250000), "2.250.000 VNĐ")
        self.assertEqual(format_vnd(0), "0 VNĐ")


class ChatBotApiTest(TestCase):
    def test_chatbot_thieu_cau_hoi(self):
        self.assertEqual(APIClient().post('/api/tro-ly-ai/', {}, format='json').status_code, 400)

    @override_settings(GEMINI_API_KEY='')
    def test_chatbot_chua_cau_hinh(self):
        res = APIClient().post('/api/tro-ly-ai/', {'cau_hoi': 'Khoa KHMT có mấy giáo viên?'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('chưa được cấu hình', res.json()['tra_loi'])
