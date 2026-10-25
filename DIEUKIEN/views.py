from rest_framework.views import APIView
from app_quan_ly.responses import success
from .services import DieuKienService


class MonTienQuyetAPI(APIView):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO
    Chức năng: Tra cứu danh sách và kiểm tra điều kiện môn tiên quyết của học phần.
    """
    def get_view_name(self):
        # Tên hiển thị to ở đầu trang giao diện Django
        return "Điều Kiện Tiên Quyết Học Phần"

    def get(self, request, MAHV, MAMH):
        res = DieuKienService.kiem_tra_dieu_kien_hoc_mon(MAHV, MAMH)
        return success(MAHV=MAHV, MAMH=MAMH, KQUA=res)



KiemTraDieuKienAPI = MonTienQuyetAPI