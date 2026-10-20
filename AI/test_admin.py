from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.core import signing
from rest_framework.exceptions import ValidationError

from app_quan_ly.management.commands.seed_data import run_seed
from .models import Phong, LichHoc
from . import admin_services


class AIAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_seed()
        cls.admin = User.objects.get(username='admin')
        cls.staff = User.objects.create_user('staff', is_staff=True)
        Phong.objects.create(MAPHONG='A101', SUCCHUA=60)

    def setUp(self):
        self.client.force_login(self.admin)
        self.url = reverse('admin:AI_lichhoc_xep_lich')

    def test_preview_and_exact_confirmation(self):
        response = self.client.post(self.url, {'action': 'preview', 'HOCKY': 1, 'NAM': 2006})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Xác nhận lưu lịch')
        self.assertEqual(LichHoc.objects.count(), 0)
        token = response.context['preview_token']
        expected = signing.loads(token, salt=admin_services.SALT)['lich']
        # Xác nhận không gọi lại solver: lưu chính xác preview.
        with patch('AI.services.xep_lich', side_effect=AssertionError('Không được giải lại')):
            saved = self.client.post(self.url, {'action': 'confirm', 'preview_token': token})
        self.assertEqual(saved.status_code, 302)
        actual = list(LichHoc.objects.values('MALOP_id', 'MAMH_id', 'MAPHONG_id', 'THU', 'CA'))
        self.assertEqual(len(actual), len(expected))
        for row in expected:
            self.assertIn({'MALOP_id': row['MALOP'], 'MAMH_id': row['MAMH'], 'MAPHONG_id': row['MAPHONG'],
                           'THU': row['THU'], 'CA': row['CA']}, actual)

    def test_reject_stale_tampered_and_other_owner(self):
        _, token = admin_services.preview(1, 2006, self.admin.pk)
        with self.assertRaises(ValidationError): admin_services.confirm(token + 'tamper', self.admin.pk)
        with self.assertRaises(ValidationError): admin_services.confirm(token, self.staff.pk)
        Phong.objects.filter(pk='A101').update(SUCCHUA=61)
        response = self.client.post(self.url, {'action': 'confirm', 'preview_token': token})
        self.assertContains(response, 'Dữ liệu đã thay đổi')
        self.assertEqual(LichHoc.objects.count(), 0)

    def test_expired_and_csrf(self):
        _, token = admin_services.preview(1, 2006, self.admin.pk)
        with patch('django.core.signing.time.time', return_value=10**12):
            with self.assertRaises(ValidationError): admin_services.confirm(token, self.admin.pk)
        c = Client(enforce_csrf_checks=True)
        c.force_login(self.admin)
        self.assertEqual(c.post(self.url, {'action': 'preview', 'HOCKY': 1, 'NAM': 2006}).status_code, 403)

    def test_permissions_and_admin_navigation(self):
        self.assertContains(self.client.get(reverse('admin:AI_lichhoc_changelist')), 'AI xếp lịch học')
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_missing_room_and_invalid_year(self):
        response = self.client.post(self.url, {'action': 'preview', 'HOCKY': 1, 'NAM': 2099})
        self.assertIsNone(response.context['preview_token'])
        Phong.objects.all().delete()
        response = self.client.post(self.url, {'action': 'preview', 'HOCKY': 1, 'NAM': 2006})
        self.assertContains(response, 'Không có phòng')
        self.assertEqual(LichHoc.objects.count(), 0)

    def test_room_admin_uses_capacity_validation(self):
        url = reverse('admin:AI_phong_add')
        response = self.client.post(url, {'MAPHONG': 'B101', 'SUCCHUA': 50, 'LOAI': 'LT', '_save': 'Lưu'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Phong.objects.filter(pk='B101').exists())
        _, token = admin_services.preview(1, 2006, self.admin.pk)
        admin_services.confirm(token, self.admin.pk)
        room = LichHoc.objects.first().MAPHONG
        response = self.client.post(reverse('admin:AI_phong_change', args=[room.pk]), {
            'MAPHONG': room.pk, 'SUCCHUA': 1, 'LOAI': 'LT', '_save': 'Lưu'})
        self.assertEqual(response.status_code, 200)
        room.refresh_from_db()
        self.assertGreater(room.SUCCHUA, 1)
        response = self.client.post(reverse('admin:AI_phong_change', args=[room.pk]), {
            'SUCCHUA': 100, 'LOAI': 'LT', '_save': 'Lưu'})
        self.assertEqual(response.status_code, 302)
        room.refresh_from_db()
        self.assertEqual(room.SUCCHUA, 100)
