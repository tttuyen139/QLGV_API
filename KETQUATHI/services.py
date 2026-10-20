from django.db.models import Max

from HOCVIEN.models import HocVien
from .models import KetQuaThi


class KetQuaThiService:
    @staticmethod
    def tinh_diem_trung_binh_hoc_vien(MAHV: str) -> dict:
        """Tính ĐTB học viên (lấy điểm cao nhất mỗi môn)"""
        hv = HocVien.objects.filter(MAHV=MAHV).first()
        if not hv:
            return None

        diem_max_cac_mon = (
            KetQuaThi.objects.filter(MAHV=MAHV)
            .values('MAMH')
            .annotate(diem_cao_nhat=Max('DIEM'))
        )

        if not diem_max_cac_mon:
            return {"MAHV": MAHV, "HOTEN": f"{hv.HO} {hv.TEN}", "dtb": 0, "xep_loai": "Chưa có kết quả thi"}

        tong_DIEM = sum(item['diem_cao_nhat'] for item in diem_max_cac_mon)
        dtb = round(float(tong_DIEM) / len(diem_max_cac_mon), 2)
        xep_loai = "Xuất sắc" if dtb >= 9.0 else "Giỏi" if dtb >= 8.0 else "Khá" if dtb >= 6.5 else "Trung bình" if dtb >= 5.0 else "Yếu"

        return {
            "MAHV": MAHV,
            "HOTEN": f"{hv.HO} {hv.TEN}",
            "so_mon_hoan_thanh": len(diem_max_cac_mon),
            "diem_trung_binh": dtb,
            "xep_loai": xep_loai
        }
