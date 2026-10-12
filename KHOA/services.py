from django.db.models import Sum

from GIAOVIEN.models import GiaoVien
from app_quan_ly.utils import format_vnd


class KhoaService:
    @staticmethod
    def tinh_quy_luong_khoa(ma_khoa: str) -> dict:
        """Tính tổng quỹ lương chi trả cho 1 Khoa"""
        ds_gv = GiaoVien.objects.filter(ma_khoa_id=ma_khoa)
        if not ds_gv.exists():
            return None

        tong_luong = ds_gv.aggregate(tong=Sum('muc_luong'))['tong']
        return {
            "ma_khoa": ma_khoa,
            "so_luong_giao_vien": ds_gv.count(),
            "tong_quy_luong": int(tong_luong),
            "tong_quy_luong_vnd": format_vnd(tong_luong)
        }
