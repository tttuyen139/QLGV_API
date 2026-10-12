from rest_framework import status
from rest_framework.views import APIView

from app_quan_ly.responses import success, error
from .services import KhoaService


class QuyLuongKhoaAPI(APIView):
    """Tính quỹ lương của Khoa"""

    def get(self, request, ma_khoa):
        res = KhoaService.tinh_quy_luong_khoa(ma_khoa)
        if not res:
            return error("Khoa không tồn tại", status.HTTP_404_NOT_FOUND)
        return success(data=res)
