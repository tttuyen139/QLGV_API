from django.db.models import Max
from app_quan_ly.models import GiaoVien, KetQuaThi, HocVien, DieuKien

class GiaoVuService:
    @staticmethod
    def tinh_quy_luong_khoa(ma_khoa: str) -> dict:
        """Tính tổng quỹ lương chi trả cho 1 Khoa"""
        ds_gv = GiaoVien.objects.filter(ma_khoa_id=ma_khoa)
        if not ds_gv.exists():
            return None

        tong_luong = sum(gv.muc_luong for gv in ds_gv)
        return {
            "ma_khoa": ma_khoa,
            "so_luong_giao_vien": ds_gv.count(),
            "tong_quy_luong": int(tong_luong),
            "tong_quy_luong_vnd": f"{int(tong_luong):,} VNĐ".replace(',', '.')
        }

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

    @staticmethod
    def kiem_tra_dieu_kien_hoc_mon(ma_hv: str, ma_mh: str) -> dict:
        """ Kiểm tra học viên có đủ điều kiện học môn (dựa vào bảng DIEUKIEN)"""
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