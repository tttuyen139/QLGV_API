from django.db.models import Sum

from GIAOVIEN.models import GiaoVien
from app_quan_ly.utils import format_vnd


class KhoaService:
    @staticmethod
    def tinh_quy_luong_khoa(MAKHOA: str) -> dict:
        """Tính tổng quỹ lương chi trả cho 1 Khoa"""
        ds_gv = GiaoVien.objects.filter(MAKHOA_id=MAKHOA)
        if not ds_gv.exists():
            return None

        tong_luong = ds_gv.aggregate(tong=Sum('MUCLUONG'))['tong']
        return {
            "MAKHOA": MAKHOA,
            "so_luong_giao_vien": ds_gv.count(),
            "tong_quy_luong": format(tong_luong, '.4f'),
            "tong_quy_luong_vnd": format_vnd(tong_luong)
        }
