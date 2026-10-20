"""DDL SQLite phục vụ demo; SQL Server luôn chạy nguyên file SQL gốc."""

import re
from pathlib import Path

TABLES = ['KHOA', 'GIAOVIEN', 'MONHOC', 'DIEUKIEN', 'LOP', 'HOCVIEN', 'GIANGDAY', 'KETQUATHI']


def sqlite_ddl():
    sql = (Path(__file__).resolve().parent.parent / 'docs/QLGV_SQL_Server.sql').read_text(
        encoding='utf-8-sig'
    )
    statements = re.findall(r'CREATE TABLE dbo\.\w+ \(.*?\n\);', sql, re.S)
    result = []
    for s in statements:
        s = s.replace('dbo.', '').replace("N'", "'")
        s = s.replace('TRGKHOA CHAR(4) NULL', 'TRGKHOA CHAR(4) NULL REFERENCES GIAOVIEN(MAGV)')
        s = s.replace('TRGLOP CHAR(5) NULL', 'TRGLOP CHAR(5) NULL REFERENCES HOCVIEN(MAHV)')
        result.append(s)
    return result
