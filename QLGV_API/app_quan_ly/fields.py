from django.db import models


class SQLCharField(models.CharField):
    def db_type(self, connection):
        return f'char({self.max_length})' if connection.vendor == 'microsoft' else super().db_type(connection)


class SQLVarCharField(models.CharField):
    def db_type(self, connection):
        return f'varchar({self.max_length})' if connection.vendor == 'microsoft' else super().db_type(connection)


class SmallDateTimeField(models.DateTimeField):
    def db_type(self, connection):
        return 'smalldatetime' if connection.vendor == 'microsoft' else super().db_type(connection)


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 19)
        kwargs.setdefault('decimal_places', 4)
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'money' if connection.vendor == 'microsoft' else super().db_type(connection)


class SQLTinyIntField(models.PositiveSmallIntegerField):
    def db_type(self, connection):
        return 'tinyint' if connection.vendor == 'microsoft' else super().db_type(connection)
