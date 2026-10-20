from KETQUATHI.models import KetQuaThi
from .models import DieuKien


class DieuKienService:
    @staticmethod
    def kiem_tra_dieu_kien_hoc_mon(MAHV: str, MAMH: str) -> dict:
        """Kiểm tra học viên có đủ điều kiện học môn (dựa vào bảng DIEUKIEN)"""
        mon_truoc = DieuKien.objects.filter(MAMH_id=MAMH).values_list('MAMH_TRUOC_id', flat=True)
        if not mon_truoc:
            return {"du_dieu_kien": True, "ly_do": "Môn học này không có môn tiên quyết."}

        for mamh_t in mon_truoc:
            passed = KetQuaThi.objects.filter(MAHV_id=MAHV, MAMH_id=mamh_t, KQUA='Đạt').exists()
            if not passed:
                return {
                    "du_dieu_kien": False,
                    "mon_chua_dat": mamh_t,
                    "ly_do": f"Chưa HOàn thành môn điều kiện: {mamh_t}"
                }

        return {"du_dieu_kien": True, "ly_do": "Đã HOàn thành đầy đủ tất cả các môn tiên quyết."}
