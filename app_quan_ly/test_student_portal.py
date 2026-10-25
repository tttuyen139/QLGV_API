from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings
from rest_framework.test import APIClient
from app_quan_ly.management.commands.seed_data import run_seed
from HOCVIEN.models import HocVien
from GIANGDAY.models import GiangDay
from AI.models import Phong, LichHoc


class StudentPortalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_seed()
        cls.hv = HocVien.objects.get(pk='K1105')
        cls.student_user = User.objects.create_user(cls.hv.pk, password='Portal-test-2026')
        cls.unlinked = User.objects.create_user('unlinked_portal', password='Portal-test-2026')
        cls.staff = User.objects.create_user('portal_staff', password='Portal-test-2026', is_staff=True)
        cls.room = Phong.objects.create(MAPHONG='PT01', SUCCHUA=100)

    def client_for_student(self):
        c = APIClient()
        c.force_authenticate(self.student_user)
        return c

    def test_anonymous_root_redirects_to_login(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/api-auth/login/', r.url)

    def test_student_login_default_destination(self):
        r = self.client.post('/api-auth/login/', {'username': self.hv.pk, 'password': 'Portal-test-2026'})
        self.assertRedirects(r, '/hoc-vien/', fetch_redirect_response=False)

    def test_staff_login_default_destination(self):
        r = self.client.post('/api-auth/login/', {'username': self.staff.username, 'password': 'Portal-test-2026'})
        self.assertRedirects(r, '/admin/', fetch_redirect_response=False)

    def test_unsafe_next_does_not_redirect_external(self):
        r = self.client.post('/api-auth/login/?next=https://evil.example/', {'username': self.hv.pk, 'password': 'Portal-test-2026'})
        self.assertRedirects(r, '/hoc-vien/', fetch_redirect_response=False)

    def test_safe_next_is_preserved(self):
        r = self.client.post('/api-auth/login/?next=/api/hoc-vien/lich-hoc/', {'username': self.hv.pk, 'password': 'Portal-test-2026'})
        self.assertRedirects(r, '/api/hoc-vien/lich-hoc/', fetch_redirect_response=False)

    def test_profile_compatibility_redirect(self):
        self.client.force_login(self.student_user)
        self.assertRedirects(self.client.get('/accounts/profile/'), '/hoc-vien/', fetch_redirect_response=False)

    def test_login_csrf_protection_and_valid_token(self):
        c = Client(enforce_csrf_checks=True)
        r = c.get('/api-auth/login/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'csrfmiddlewaretoken')
        data = {'username': self.hv.pk, 'password': 'Portal-test-2026'}
        self.assertEqual(c.post('/api-auth/login/', data).status_code, 403)
        data['csrfmiddlewaretoken'] = c.cookies['csrftoken'].value
        self.assertRedirects(c.post('/api-auth/login/', data), '/hoc-vien/', fetch_redirect_response=False)

    def test_home_links_are_available(self):
        c = self.client_for_student()
        r = c.get('/api/hoc-vien/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['hoc_vien']['MAHV'], self.hv.pk)
        self.assertEqual(len(r.data['chuc_nang']), 7)
        for url in r.data['chuc_nang'].values():
            self.assertEqual(c.get(url).status_code, 200, url)

    def test_unlinked_student_is_rejected(self):
        c = APIClient(); c.force_authenticate(self.unlinked)
        for url in ['/api/hoc-vien/', '/api/hoc-vien/lich-hoc/', '/api/hoc-vien/diem-trung-binh/', '/api/hoc-vien/goi-y-hoc-phan/']:
            self.assertEqual(c.get(url).status_code, 403)

    def test_personal_schedule_excludes_other_students(self):
        assignments = list(GiangDay.objects.all())
        own = next(g for g in assignments if g.MALOP_id == self.hv.MALOP_id)
        others = [g for g in assignments if g.MALOP_id != self.hv.MALOP_id]
        def make(g, registrations):
            return LichHoc.objects.create(MALOP_id=g.MALOP_id, MAMH_id=g.MAMH_id,
                MAPHONG=self.room, THU=2, CA=1, SISO_TOIDA=100, DANGKY=registrations)
        a = make(own, [])
        b = make(others[0], [self.hv.pk])
        hidden = make(others[1], ['SOMEONE_ELSE'])
        r = self.client_for_student().get('/api/hoc-vien/lich-hoc/?MAHV=SOMEONE_ELSE')
        self.assertEqual({x['id'] for x in r.data['lich_hoc']}, {a.pk, b.pk})
        self.assertNotIn(hidden.pk, {x['id'] for x in r.data['lich_hoc']})
        self.assertTrue(all('DANGKY' not in x for x in r.data['lich_hoc']))

    def test_average_uses_logged_in_student(self):
        r = self.client_for_student().get('/api/hoc-vien/diem-trung-binh/?MAHV=OTHER')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['MAHV'], self.hv.pk)

    def test_prerequisite_unknown_course(self):
        r = self.client_for_student().get('/api/hoc-vien/mon-tien-quyet/?MAMH=DOESNOTEXIST')
        self.assertEqual(r.status_code, 404)

    def test_browsable_post_pages_render(self):
        c = self.client_for_student()
        for path in ['goi-y-hoc-phan', 'xac-nhan-dang-ky', 'tro-ly']:
            r = c.get('/api/hoc-vien/' + path + '/', HTTP_ACCEPT='text/html')
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, 'POST')
            self.assertContains(r, 'csrfmiddlewaretoken')

    def test_confirmation_reuses_validation(self):
        c = self.client_for_student()
        self.assertEqual(c.post('/api/hoc-vien/xac-nhan-dang-ky/', {'lich_hoc': []}, format='json').status_code, 400)
        self.assertEqual(c.post('/api/hoc-vien/xac-nhan-dang-ky/', {'lich_hoc': [1, 1]}, format='json').status_code, 400)

    @patch('AI.views.services.xac_nhan')
    def test_confirmation_uses_session_identity(self, confirm):
        confirm.return_value = {'da_dang_ky': [1]}
        r = self.client_for_student().post('/api/hoc-vien/xac-nhan-dang-ky/', {'lich_hoc': [1], 'MAHV': 'OTHER'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(confirm.call_args.args[0].pk, self.hv.pk)

    @override_settings(GEMINI_API_KEY='')
    def test_chat_without_key(self):
        c = self.client_for_student()
        self.assertEqual(c.post('/api/hoc-vien/tro-ly/', {}, format='json').status_code, 400)
        r = c.post('/api/hoc-vien/tro-ly/', {'cau_hoi': 'Có những khoa nào?'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('chưa được cấu hình', r.data['tra_loi'])


    def test_dashboard_menu_and_forms(self):
        self.client.force_login(self.student_user)
        r = self.client.get('/hoc-vien/')
        for text in ['Lịch học', 'Lớp của tôi', 'Kết quả thi', 'Đăng ký học phần', 'suggest-form', 'csrfmiddlewaretoken']:
            self.assertContains(r, text)

    def test_old_html_api_home_redirects_to_dashboard(self):
        self.client.force_login(self.student_user)
        self.assertRedirects(self.client.get('/api/hoc-vien/', HTTP_ACCEPT='text/html'), '/hoc-vien/')

    def test_unlinked_dashboard(self):
        self.client.force_login(self.unlinked)
        self.assertContains(self.client.get('/hoc-vien/'), 'Tài khoản chưa liên kết', status_code=403)

    def test_staff_dashboard(self):
        self.client.force_login(self.staff)
        self.assertRedirects(self.client.get('/hoc-vien/'), '/admin/', fetch_redirect_response=False)

    def test_class_privacy(self):
        r = self.client_for_student().get('/api/hoc-vien/lop/?MALOP=K12')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['MALOP'], self.hv.MALOP_id)

    def test_results_privacy(self):
        r = self.client_for_student().get('/api/hoc-vien/ket-qua-thi/?MAHV=K1201')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(all(x['MAHV'] == self.hv.pk for x in r.data['ket_qua_thi']))

    def test_catalog_registration_privacy(self):
        g = GiangDay.objects.first()
        LichHoc.objects.create(MALOP_id=g.MALOP_id, MAMH_id=g.MAMH_id,
            MAPHONG=self.room, THU=2, CA=1, SISO_TOIDA=100, DANGKY=['OTHER'])
        r = self.client_for_student().get('/api/hoc-vien/hoc-phan/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['total'], 1)
        row = r.data['hoc_phan'][0]
        self.assertNotIn('DANGKY', row)
        self.assertIn('CHO_TRONG', row)
        self.assertEqual(row['HOCKY'], g.HOCKY)

    def test_new_read_only_endpoints(self):
        c = self.client_for_student()
        for name in ['lop', 'ket-qua-thi', 'hoc-phan']:
            self.assertEqual(c.post('/api/hoc-vien/'+name+'/', {}, format='json').status_code, 405)

    def test_logout_post(self):
        self.client.force_login(self.student_user)
        self.assertEqual(self.client.get('/hoc-vien/dang-xuat/').status_code, 405)
        self.assertRedirects(self.client.post('/hoc-vien/dang-xuat/'), '/api-auth/login/', fetch_redirect_response=False)
        self.assertEqual(self.client.get('/hoc-vien/').status_code, 302)


    @patch('AI.views.services.goi_y')
    @patch('AI.views.giai_thich', return_value='Giải thích')
    @patch('AI.views.phan_tich_yeu_cau')
    def test_explicit_credit_fields_keep_ai_preferences(self, parse, explain, recommend):
        parse.return_value = ({'tin_chi_min':12, 'tin_chi_max':20, 'thu_tranh':[7],
                               'ca_uu_tien':[1], 'ma_mon_uu_tien':[]}, True)
        recommend.return_value = {'de_xuat':[], 'tong_tin_chi':0, 'ghi_chu':'', 'toi_uu':False}
        r = self.client_for_student().post('/api/hoc-vien/goi-y-hoc-phan/',
            {'HOCKY':1, 'NAM':2006, 'yeu_cau':'Tránh thứ 7',
             'so_thich':{'tin_chi_min':0,'tin_chi_max':18}}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(recommend.call_args.args[3]['thu_tranh'], [7])
        self.assertEqual(recommend.call_args.args[3]['tin_chi_max'], 18)
