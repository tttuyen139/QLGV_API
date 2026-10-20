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


class MigrationScriptTest(TestCase):
    def _module(self):
        import importlib.util
        from django.conf import settings
        spec = importlib.util.spec_from_file_location('legacy_test', settings.BASE_DIR/'scripts/migrate_legacy_sqlite.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_original_invalid_source_is_not_changed(self):
        import hashlib
        import tempfile
        from pathlib import Path
        from django.conf import settings
        source=settings.BASE_DIR/'db.sqlite3'
        before=hashlib.sha256(source.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'target.sqlite3'
            with self.assertRaises(ValueError): self._module().migrate(source,target)
            self.assertFalse(target.exists())
            import json
            report=json.loads(Path(str(target)+'.blocked.json').read_text())
            self.assertEqual(len(report['blocked']),2)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)

    def test_valid_copy_migrates_all_rows_and_keeps_old_ids(self):
        import sqlite3
        import tempfile
        from pathlib import Path
        from django.conf import settings
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'fixture.sqlite3';target=Path(d)/'target.sqlite3'
            original=sqlite3.connect((settings.BASE_DIR/'db.sqlite3').as_uri()+'?mode=ro',uri=True)
            fixture=sqlite3.connect(src);original.backup(fixture);original.close()
            # Chỉ tạo fixture hợp lệ trong temp; không sửa bản ghi của người dùng.
            fixture.execute('DELETE FROM DIEUKIEN')
            fixture.execute("UPDATE KETQUATHI SET ket_qua='Đạt' WHERE diem>=5")
            fixture.commit();fixture.close()
            result=self._module().migrate(src,target)
            self.assertTrue(result['content_verified'])
            self.assertEqual(result['rows_before'],result['rows_after'])
            self.assertTrue(result['legacy_id_mapping']['KETQUATHI'])
            check=sqlite3.connect(target)
            self.assertEqual(check.execute('PRAGMA foreign_key_check').fetchall(),[])
            self.assertEqual(check.execute("SELECT KQUA FROM KETQUATHI").fetchone()[0],'Đạt')
            check.close()
