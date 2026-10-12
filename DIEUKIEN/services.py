from KETQUATHI.models import KetQuaThi
from .models import DieuKien


class DieuKienService:
    @staticmethod
    def kiem_tra_dieu_kien_hoc_mon(ma_hv: str, ma_mh: str) -> dict:
        """Kiểm tra học viên có đủ điều kiện học môn (dựa vào bảng DIEUKIEN)"""
        mon_truoc = DieuKien.objects.filter(ma_mh_id=ma_mh).values_list('ma_mh_truoc_id', flat=True)
        if not mon_truoc:
            return {"du_dieu_kien": True, "ly_do": "Môn học này không có môn tiên quyết."}

        for mamh_t in mon_truoc:
            passed = KetQuaThi.objects.filter(ma_hv_id=ma_hv, ma_mh_id=mamh_t, ket_qua='Đạt').exists()
            if not passed:
                return {
                    "du_dieu_kien": False,
                    "mon_chua_dat": mamh_t,
                    "ly_do": f"Chưa hoàn thành môn điều kiện: {mamh_t}"
                }

        return {"du_dieu_kien": True, "ly_do": "Đã hoàn thành đầy đủ tất cả các môn tiên quyết."}
