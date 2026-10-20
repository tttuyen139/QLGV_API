"""Copy dữ liệu nghiệp vụ từ SQLite cũ sang DB cấu hình hiện tại (có thể SQL Server)."""

import importlib.util
import sqlite3
from datetime import datetime
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from app_quan_ly.schema_tools import TABLES, sqlite_ddl


class Command(BaseCommand):
    help = 'Import BRD vào DB đích trống; mặc định dry-run. Không chép tài khoản hệ thống sang SQL Server.'

    def add_arguments(self, parser):
        parser.add_argument('--source', required=True)
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, **options):
        path = Path(options['source']).resolve()
        if not path.is_file():
            raise CommandError('Không tìm thấy SQLite nguồn.')
        if connection.vendor == 'sqlite' and path == Path(connection.settings_dict['NAME']).resolve():
            raise CommandError('Nguồn phải khác database đích.')
        spec = importlib.util.spec_from_file_location(
            'legacy', settings.BASE_DIR / 'scripts/migrate_legacy_sqlite.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
        snapshot = sqlite3.connect(':memory:')
        source.backup(snapshot)
        source.close()
        try:
            rows, ids = module.transformed(snapshot)
            # Preflight tất cả CHECK/FK bằng DDL chuẩn trước khi kết nối ghi DB đích.
            tmp = sqlite3.connect(':memory:')
            for sql in sqlite_ddl():
                tmp.execute(sql)
            for table in TABLES:
                for row in rows[table]:
                    tmp.execute(
                        f'INSERT INTO "{table}" ('
                        + ','.join('"' + c + '"' for c in row)
                        + ') VALUES ('
                        + ','.join('?' for c in row)
                        + ')',
                        list(row.values()),
                    )
            if tmp.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Foreign key preflight thất bại')
            tmp.close()
        except Exception as exc:
            raise CommandError(f'Preflight thất bại; không ghi dữ liệu: {exc}')
        finally:
            snapshot.close()
        import json

        metadata = json.loads((settings.BASE_DIR / 'docs/schema.json').read_text())
        models = {t: apps.get_model(t, c) for t, c in metadata['classes'].items()}
        from AI.models import Phong

        try:
            with transaction.atomic():
                if connection.vendor == 'microsoft':
                    # Khóa các bảng đích kể cả khi rỗng; tránh import đồng thời.
                    with connection.cursor() as cursor:
                        for t in TABLES:
                            cursor.execute(f'SELECT COUNT(*) FROM [{t}] WITH (TABLOCKX, HOLDLOCK)')
                else:
                    list(Phong.objects.select_for_update().all())
                if any(m.objects.exists() for m in models.values()):
                    raise CommandError('Cả 8 bảng đích phải trống. Không merge/ghi đè seed hoặc dữ liệu cũ.')
                refs = []
                for table in TABLES:
                    model = models[table]
                    for row in rows[table]:
                        values = {}
                        for name, value in row.items():
                            field = model._meta.get_field(name)
                            if field.is_relation:
                                if name in ('TRGKHOA', 'TRGLOP') and value is not None:
                                    refs.append((model, row[model._meta.pk.name], field.attname, value))
                                    value = None
                                values[field.attname] = value
                            else:
                                values[name] = (
                                    datetime.fromisoformat(value)
                                    if name in ('NGTLAP', 'NGSINH', 'NGVL', 'TUNGAY', 'DENNGAY', 'NGTHI')
                                    else value
                                )
                        model.objects.create(**values)
                for model, key, field, value in refs:
                    model.objects.filter(pk=key).update(**{field: value})
                # Đối chiếu từng trường, không chỉ COUNT.
                for table in TABLES:
                    model = models[table]
                    for row in rows[table]:
                        keys = metadata['keys'].get(table, [model._meta.pk.name])
                        obj = model.objects.get(**{model._meta.get_field(k).attname: row[k] for k in keys})
                        for name, value in row.items():
                            actual = getattr(obj, model._meta.get_field(name).attname)
                            if isinstance(actual, datetime):
                                actual = actual.isoformat(sep=' ')
                            # CHAR trên SQL Server có thể được padding; không loại bỏ ký tự gốc khác.
                            if isinstance(actual, str) and actual.rstrip(' ') == str(value):
                                actual = value
                            if name in ('HESO', 'MUCLUONG', 'DIEM'):
                                from decimal import Decimal

                                if Decimal(str(actual)) != Decimal(str(value)):
                                    raise ValueError(f'Sai lệch {table}.{name}')
                            elif actual != value:
                                raise ValueError(f'Sai lệch {table}.{name}')
                    if model.objects.count() != len(rows[table]):
                        raise ValueError(f'Sai số lượng {table}')
                if not options['apply']:
                    transaction.set_rollback(True)
        except (ValueError, sqlite3.Error) as exc:
            raise CommandError(f'Import rollback: {exc}')
        self.stdout.write(
            'Đã đối chiếu toàn bộ dữ liệu. '
            + ('COMMIT thành công.' if options['apply'] else 'DRY-RUN: toàn bộ ghi thử đã rollback.')
        )
        self.stdout.write(
            'Tài khoản/nhóm/quyền: dùng dumpdata/loaddata có kiểm tra riêng; xem MIGRATION.md. Giữ SQLite nguồn và báo cáo old id để tra cứu.'
        )
