from rest_framework import status
from rest_framework.views import APIView

from rest_framework import serializers
from app_quan_ly.responses import success, error, BaseListAPI
from .services import KhoaService
from .models import Khoa
from .serializers import KhoaSerializer

class QuyLuongKhoaAPI(APIView):
    """Tính quỹ lương của Khoa"""

    def get(self, request, MAKHOA):
        res = KhoaService.tinh_quy_luong_khoa(MAKHOA)
        if not res:
            return error("Khoa không tồn tại", status.HTTP_404_NOT_FOUND)
        return success(data=res)


class KhoaListAPI(BaseListAPI):
    queryset = Khoa.objects.all()
    serializer_class = KhoaSerializer

