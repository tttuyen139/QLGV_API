from rest_framework import status
from rest_framework.views import APIView
from app_quan_ly.responses import success, error, BaseListAPI
from .services import KhoaService
from .models import Khoa
from .serializers import KhoaSerializer


class ThongKeLuongKhoaAPI(APIView):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO

    """
    def get_view_name(self):
        # Tên hiển thị to ở đầu trang giao diện Django
        return "Thống Kê Thù Lao Giảng Dạy"

    def get(self, request, MAKHOA):
        res = KhoaService.tinh_quy_luong_khoa(MAKHOA)
        if not res:
            return error("Khoa không tồn tại", status.HTTP_404_NOT_FOUND)
        return success(data=res)



QuyLuongKhoaAPI = ThongKeLuongKhoaAPI


class KhoaListAPI(BaseListAPI):
    queryset = Khoa.objects.all()
    serializer_class = KhoaSerializer