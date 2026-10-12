from django.db.models import Max

from HOCVIEN.models import HocVien
from .models import KetQuaThi


class KetQuaThiService:
    @staticmethod
    def tinh_diem_trung_binh_hoc_vien(ma_hv: str) -> dict:
        """Tính ĐTB học viên (lấy điểm cao nhất mỗi môn)"""
        hv = HocVien.objects.filter(ma_hv=ma_hv).first()
        if not hv:
            return None

        diem_max_cac_mon = (
            KetQuaThi.objects.filter(ma_hv=ma_hv)
            .values('ma_mh')
            .annotate(diem_cao_nhat=Max('diem'))
        )

        if not diem_max_cac_mon:
            return {"ma_hv": ma_hv, "ho_ten": f"{hv.ho} {hv.ten}", "dtb": 0, "xep_loai": "Chưa có kết quả thi"}

        tong_diem = sum(item['diem_cao_nhat'] for item in diem_max_cac_mon)
        dtb = round(float(tong_diem) / len(diem_max_cac_mon), 2)
        xep_loai = "Xuất sắc" if dtb >= 9.0 else "Giỏi" if dtb >= 8.0 else "Khá" if dtb >= 6.5 else "Trung bình" if dtb >= 5.0 else "Yếu"

        return {
            "ma_hv": ma_hv,
            "ho_ten": f"{hv.ho} {hv.ten}",
            "so_mon_hoan_thanh": len(diem_max_cac_mon),
            "diem_trung_binh": dtb,
            "xep_loai": xep_loai
        }
