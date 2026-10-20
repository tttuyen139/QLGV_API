from django.test.runner import DiscoverRunner
from django.db import connection
from .schema_tools import sqlite_ddl


class QLGVTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)
        if connection.vendor != 'sqlite':
            raise RuntimeError('Test runner này chỉ dùng database SQLite kiểm thử riêng.')
        with connection.cursor() as cursor:
            for sql in sqlite_ddl():
                cursor.execute(sql)
        return result
