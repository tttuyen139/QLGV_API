from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from app_quan_ly.management.commands.seed_data import run_seed
from HOCVIEN.models import HocVien
from GIANGDAY.models import GiangDay
from KETQUATHI.models import KetQuaThi
from .models import Phong, LichHoc
from .services import xep_lich, goi_y, xac_nhan, kiem_tra, _ds_gd


class AIFlowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_seed()
        Phong.objects.create(MAPHONG='A101', SUCCHUA=60)
        Phong.objects.create(MAPHONG='A102', SUCCHUA=60)
        cls.user = User.objects.create_user('K1105', password='testpassword')

    def test_preview_does_not_write(self):
        result = xep_lich(1, 2006)
        self.assertTrue(result['thanh_cong'])
        self.assertEqual(LichHoc.objects.count(), 0)

    def test_saved_schedule_has_no_conflicts(self):
        self.assertTrue(xep_lich(1, 2006, True)['thanh_cong'])
        rows = list(LichHoc.objects.all())
        gd = _ds_gd()
        self.assertEqual(len(rows), 6)
        for a in rows:
            for b in rows:
                if a.pk >= b.pk:
                    continue
                g, h = gd[a.MALOP_id, a.MAMH_id], gd[b.MALOP_id, b.MAMH_id]
                if g.TUNGAY <= h.DENNGAY and h.TUNGAY <= g.DENNGAY and (a.THU, a.CA) == (b.THU, b.CA):
                    self.assertNotEqual(a.MAPHONG_id, b.MAPHONG_id)
                    self.assertNotEqual(g.MAGV_id, h.MAGV_id)
                    self.assertNotEqual(g.MALOP_id, h.MALOP_id)

    def test_no_rooms_is_infeasible(self):
        Phong.objects.all().delete()
        self.assertFalse(xep_lich(1, 2006)['thanh_cong'])

    def _make_schedule(self):
        for g in GiangDay.objects.filter(HOCKY=1, NAM=2006):
            LichHoc.objects.create(
                MALOP_id=g.MALOP_id,
                MAMH_id=g.MAMH_id,
                MAPHONG_id='A101',
                THU=2 if g.MAMH_id == 'THDC' else 3,
                CA=1,
                SISO_TOIDA=60,
            )

    def test_recommendation_does_not_write(self):
        self._make_schedule()
        hv = HocVien.objects.get(pk='K1105')
        # Môn mở cho K12 nhưng K11 đã có cùng môn -> không đề xuất trùng.
        result = goi_y(
            hv,
            1,
            2006,
            {'tin_chi_min': 0, 'tin_chi_max': 20, 'thu_tranh': [], 'ca_uu_tien': [], 'ma_mon_uu_tien': []},
        )
        self.assertEqual(result['de_xuat'], [])
        self.assertTrue(all(l.DANGKY == [] for l in LichHoc.objects.all()))

    def test_all_prerequisites_and_pass_threshold(self):
        self.assertTrue(xep_lich(2, 2006, True)['thanh_cong'])
        l = LichHoc.objects.get(MALOP_id='K12', MAMH_id='CSDL')
        hv = HocVien.objects.get(pk='K1105')
        with self.assertRaises(ValidationError):
            kiem_tra(hv, l, _ds_gd(), [])
        for m in ['CTRR', 'CTDLGT']:
            KetQuaThi.objects.create(
                MAHV=hv, MAMH_id=m, LANTHI=1, NGTHI=datetime(2006, 5, 1), DIEM=5, KQUA='Đạt'
            )
        kiem_tra(hv, l, _ds_gd(), [])

    def test_confirmation_rollback_and_duplicate(self):
        xep_lich(1, 2006, True)
        # Học viên K13 vốn đã có THDC/CTRR, mọi yêu cầu đăng ký lại phải bị từ chối.
        hv = HocVien.objects.get(pk='K1305')
        ids = list(LichHoc.objects.values_list('id', flat=True))[:2]
        with self.assertRaises(ValidationError):
            xac_nhan(hv, ids)
        self.assertTrue(all(l.DANGKY == [] for l in LichHoc.objects.all()))
        with self.assertRaises(ValidationError):
            xac_nhan(hv, [ids[0], ids[0]])

    def test_registration_success_and_retry(self):
        # K1105 đăng ký DHMT của K13; đã đạt THDC, chưa có lớp DHMT của K11 trong năm 2006.
        hv = HocVien.objects.get(pk='K1105')
        KetQuaThi.objects.create(
            MAHV=hv, MAMH_id='THDC', LANTHI=1, NGTHI=datetime(2006, 5, 20), DIEM=5, KQUA='Đạt'
        )
        xep_lich(3, 2006, True)
        l = LichHoc.objects.get(MALOP_id='K13', MAMH_id='DHMT')
        result = xac_nhan(hv, [l.pk])
        self.assertEqual(result['da_dang_ky'], [l.pk])
        l.refresh_from_db()
        self.assertIn(hv.pk, l.DANGKY)
        with self.assertRaises(ValidationError):
            xac_nhan(hv, [l.pk])

    def test_permissions_and_unknown_ids(self):
        c = APIClient()
        self.assertIn(c.post('/api/ai/xep-lich/', {'HOCKY': 1, 'NAM': 2006}).status_code, [401, 403])
        c.force_authenticate(self.user)
        self.assertEqual(c.post('/api/ai/xep-lich/', {'HOCKY': 1, 'NAM': 2006}).status_code, 403)
        self.assertEqual(
            c.post('/api/ai/xac-nhan-dang-ky/', {'lich_hoc': [99999]}, format='json').status_code, 400
        )
        self.assertEqual(
            c.post('/api/ai/xac-nhan-dang-ky/', {'lich_hoc': [1, 1]}, format='json').status_code, 400
        )

    def test_core_validation_composite_endpoint(self):
        c = APIClient()
        c.force_authenticate(User.objects.get(username='admin'))
        self.assertEqual(c.get('/api/du-lieu/ketquathi/K1101/CSDL/1/').status_code, 200)
        data = {
            'MAHV': 'K1105',
            'MAMH': 'THDC',
            'LANTHI': 1,
            'NGTHI': '2006-05-20T00:00:00',
            'DIEM': '4.00',
            'KQUA': 'Đạt',
        }
        self.assertEqual(c.post('/api/du-lieu/ketquathi/', data, format='json').status_code, 400)
        data['KQUA'] = 'Không đạt'
        self.assertEqual(c.post('/api/du-lieu/ketquathi/', data, format='json').status_code, 201)

    def test_batch_rolls_back_after_first_valid_registration(self):
        hv = HocVien.objects.get(pk='K1105')
        KetQuaThi.objects.create(
            MAHV=hv, MAMH_id='THDC', LANTHI=1, NGTHI=datetime(2006, 5, 20), DIEM=5, KQUA='Đạt'
        )
        a = LichHoc.objects.create(
            MALOP_id='K13', MAMH_id='DHMT', MAPHONG_id='A101', THU=2, CA=1, SISO_TOIDA=60
        )
        b = LichHoc.objects.create(
            MALOP_id='K13', MAMH_id='CSDL', MAPHONG_id='A102', THU=3, CA=1, SISO_TOIDA=60
        )
        with self.assertRaises(ValidationError):
            xac_nhan(hv, [a.pk, b.pk])
        a.refresh_from_db()
        self.assertEqual(a.DANGKY, [])

    def test_capacity_and_room_shrink_are_checked(self):
        hv = HocVien.objects.get(pk='K1105')
        KetQuaThi.objects.create(
            MAHV=hv, MAMH_id='THDC', LANTHI=1, NGTHI=datetime(2006, 5, 20), DIEM=5, KQUA='Đạt'
        )
        l = LichHoc.objects.create(
            MALOP_id='K13', MAMH_id='DHMT', MAPHONG_id='A101', THU=2, CA=1, SISO_TOIDA=12
        )
        with self.assertRaises(ValidationError):
            xac_nhan(hv, [l.pk])
        c = APIClient()
        c.force_authenticate(User.objects.get(username='admin'))
        self.assertEqual(c.patch('/api/phong/A101/', {'SUCCHUA': 5}, format='json').status_code, 400)

    def test_invalid_preferences_and_impersonation(self):
        c = APIClient()
        c.force_authenticate(self.user)
        data = {'HOCKY': 1, 'NAM': 2006, 'MAHV': 'K1101', 'so_thich': {'tin_chi_min': 20, 'tin_chi_max': 12}}
        self.assertEqual(c.post('/api/ai/goi-y-dang-ky/', data, format='json').status_code, 400)
        stranger = User.objects.create_user('unlinked', password='testpassword')
        c.force_authenticate(stranger)
        self.assertEqual(
            c.post(
                '/api/ai/goi-y-dang-ky/', {'HOCKY': 1, 'NAM': 2006, 'MAHV': 'K1101'}, format='json'
            ).status_code,
            403,
        )
