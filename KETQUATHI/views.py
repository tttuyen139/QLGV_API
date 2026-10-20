from rest_framework import status
from rest_framework.views import APIView

from app_quan_ly.responses import success, error
from .services import KetQuaThiService


class DiemTrungBinhHocVienAPI(APIView):
    """Tính điểm TB tích lũy"""

    def get(self, request, MAHV):
        res = KetQuaThiService.tinh_diem_trung_binh_hoc_vien(MAHV)
        if not res:
            return error("Học viên không tồn tại", status.HTTP_404_NOT_FOUND)
        return success(data=res)
