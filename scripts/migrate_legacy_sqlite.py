"""Chuyển SQLite cũ sang file mới; không sửa source. Chạy khi đã dừng server."""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_quan_ly.schema_tools import TABLES, sqlite_ddl


def transformed(source):
    schema = json.loads((ROOT / 'docs/schema.json').read_text())
    mapping = json.loads((ROOT / 'docs/mapping.json').read_text())
    inverse = {v: k for k, v in mapping.items()}
    result = {}
    ids = {}
    source.row_factory = sqlite3.Row
    for table in TABLES:
        cols = [r[1] for r in source.execute(f'PRAGMA table_info("{table}")')]
        if not cols:
            raise ValueError(f'Thiếu bảng nguồn {table}')
        rows = []
        ids[table] = []
        for record in source.execute(f'SELECT * FROM "{table}"'):
            record = dict(record)
            row = {}
            for f in schema['fields'][table]:
                n, kind = f[:2]
                old = inverse[n]
                candidate = n if n in record else old + '_id' if kind == 'fk' else old
                if candidate not in record:
                    if n == 'TRGLOP':
                        row[n] = None
                        continue
                    raise ValueError(f'Thiếu cột {table}.{candidate}')
                value = record[candidate]
                if kind == 'date' and value is not None:
                    dt = datetime.fromisoformat(str(value))
                    if dt.tzinfo:
                        raise ValueError(f'{table}.{n}: không tự bỏ múi giờ')
                    if (
                        not datetime(1900, 1, 1) <= dt <= datetime(2079, 6, 6, 23, 59)
                        or dt.second
                        or dt.microsecond
                    ):
                        raise ValueError(f'{table}.{n}: ngoài phạm vi SMALLDATETIME/phút')
                    value = dt.isoformat(sep=' ')
                if kind in ('char', 'varchar', 'nvarchar') and value is not None and len(str(value)) > f[2]:
                    raise ValueError(f'{table}.{n}: vượt độ dài; không cắt dữ liệu')
                if kind == 'tiny' and not (isinstance(value, int) and 0 <= value <= 255):
                    raise ValueError(f'{table}.{n}: ngoài TINYINT')
                if kind == 'small' and not (isinstance(value, int) and -32768 <= value <= 32767):
                    raise ValueError(f'{table}.{n}: ngoài SMALLINT')
                if kind in ('decimal', 'money'):
                    d = Decimal(str(value))
                    digits, scale = f[2] if kind == 'decimal' else (19, 4)
                    if d != d.quantize(Decimal(10) ** -scale) or abs(d) >= Decimal(10) ** (digits - scale):
                        raise ValueError(f'{table}.{n}: sẽ mất độ chính xác')
                    if kind == 'money' and abs(d) > Decimal('922337203685477.5807'):
                        raise ValueError('Vượt phạm vi MONEY')
                row[n] = value
            if 'id' in record:
                ids[table].append(
                    {'old_id': record['id'], 'new_key': {k: row[k] for k in schema['keys'][table]}}
                )
            known = set()
            for f in schema['fields'][table]:
                n, kind = f[:2]
                old = inverse[n]
                known.add(n if n in record else old + '_id' if kind == 'fk' else old)
            unknown = set(record) - known - {'id'}
            if unknown:
                raise ValueError(f'{table}: cột chưa có mapping {sorted(unknown)}; dừng để không mất dữ liệu')
            rows.append(row)
        result[table] = rows
    return result, ids


def digest_rows(rows):
    return hashlib.sha256(
        json.dumps(
            sorted([json.dumps(r, ensure_ascii=False, sort_keys=True, default=str) for r in rows]),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()


def migrate(source_path, target_path):
    source_path = Path(source_path).resolve()
    target_path = Path(target_path).resolve()
    if source_path == target_path or target_path.exists():
        raise ValueError('Đích phải là đường dẫn mới, không được ghi đè.')
    if not source_path.is_file():
        raise ValueError('Không tìm thấy database nguồn')
    report_path = Path(str(target_path) + '.migration.json')
    if report_path.exists():
        raise ValueError('Báo cáo đích đã tồn tại')
    # SQLite backup API tạo snapshot nhất quán, bao gồm WAL đã commit.
    src = sqlite3.connect(source_path.as_uri() + '?mode=ro', uri=True)
    fd, tmp = tempfile.mkstemp(prefix='qlgv_', suffix='.sqlite3', dir=target_path.parent)
    os.close(fd)
    dst = sqlite3.connect(tmp)
    try:
        src.backup(dst)
        rows, ids = transformed(dst)
        before = {t: len(rows[t]) for t in TABLES}
        dst.execute('PRAGMA foreign_keys=OFF')
        dst.execute('BEGIN IMMEDIATE')
        for t in reversed(TABLES):
            dst.execute(f'DROP TABLE "{t}"')
        for sql in sqlite_ddl():
            dst.execute(sql)
        blocked = []
        for t in TABLES:
            for row in rows[t]:
                cols = list(row)
                try:
                    dst.execute(
                        f'INSERT INTO "{t}" ('
                        + ','.join('"' + c + '"' for c in cols)
                        + ') VALUES ('
                        + ','.join('?' for c in cols)
                        + ')',
                        list(row.values()),
                    )
                except sqlite3.IntegrityError as exc:
                    blocked.append({'table': t, 'record': row, 'reason': str(exc)})
        if blocked:
            blocked_path = Path(str(target_path) + '.blocked.json')
            if blocked_path.exists():
                raise ValueError('Báo cáo blocked đã có; chọn tên đích khác')
            blocked_path.write_text(
                json.dumps(
                    {'blocked': blocked, 'source_rows_preserved': rows, 'legacy_id_mapping': ids},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            raise ValueError(
                f'{len(blocked)} bản ghi không hợp lệ; xem {blocked_path.name}. Chưa tạo database đích.'
            )
        issues = dst.execute('PRAGMA foreign_key_check').fetchall()
        if issues:
            raise ValueError(f'Foreign key check thất bại: {issues}')
        verified = {}
        hashes = {}
        for t in TABLES:
            actual = [dict(r) for r in dst.execute(f'SELECT * FROM "{t}"')]
            if actual != rows[t]:
                # So sánh không phụ thuộc thứ tự bản ghi/cột; số SQLite có thể chuẩn hóa 1.00 thành 1.
                def norm(items):
                    return sorted(
                        [
                            tuple(
                                (k, str(Decimal(str(v)).normalize()) if isinstance(v, (int, float)) else v)
                                for k, v in sorted(r.items())
                            )
                            for r in items
                        ],
                        key=repr,
                    )

                if norm(actual) != norm(rows[t]):
                    raise ValueError(f'Đối chiếu nội dung {t} thất bại')
            verified[t] = len(actual)
            hashes[t] = digest_rows(actual)
        if before != verified:
            raise ValueError('Số lượng bản ghi không khớp')
        if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Integrity check thất bại')
        dst.commit()
        dst.close()
        src.close()
        report = {
            'source': str(source_path),
            'target': str(target_path),
            'rows_before': before,
            'rows_after': verified,
            'content_verified': True,
            'sha256_canonical_rows': hashes,
            'legacy_id_mapping': ids,
            'notes': [
                'TRGLOP không có trong DB cũ được để NULL, không đoán lớp trưởng.',
                'Giữ nguyên các bảng hệ thống, tài khoản và mật khẩu băm trong bản sao.',
                'Không chạy seed_data sau migration. Source không bị sửa.',
            ],
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(tmp, target_path)
        return report
    except Exception:
        dst.close()
        src.close()
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--target', required=True)
    args = parser.parse_args()
    try:
        r = migrate(args.source, args.target)
        print(
            json.dumps(
                {'content_verified': r['content_verified'], 'rows': r['rows_after']}, ensure_ascii=False
            )
        )
    except Exception as exc:
        parser.exit(1, f'Migration dừng; database nguồn không đổi: {exc}\n')
