from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from app_quan_ly.schema_tools import TABLES, sqlite_ddl


class Command(BaseCommand):
    help = 'Tạo 8 bảng chuẩn cho SQLite mới. SQL Server: chạy SQL gốc trong SSMS.'

    def handle(self, *args, **options):
        if connection.vendor != 'sqlite':
            raise CommandError('SQL Server: dùng docs/QLGV_SQL_Server.sql, không tạo DDL từ ORM.')
        if set(TABLES) & set(connection.introspection.table_names()):
            raise CommandError('Đã có bảng BRD; không thay đổi hoặc ghi đè.')
        with transaction.atomic():
            with connection.cursor() as cursor:
                for sql in sqlite_ddl():
                    cursor.execute(sql)
        self.stdout.write(self.style.SUCCESS('Đã tạo đúng 8 bảng BRD; chưa nạp dữ liệu.'))
