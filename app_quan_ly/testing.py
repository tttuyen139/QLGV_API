import contextlib
import io

from .management.commands.seed_data import run_seed


class SeedDataMixin:
    """Nạp dữ liệu mẫu một lần cho mỗi TestCase"""

    @classmethod
    def setUpTestData(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            run_seed()
