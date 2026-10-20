from rest_framework.views import APIView

from app_quan_ly.responses import success
from .services import DieuKienService


class KiemTraDieuKienAPI(APIView):
    """GET: Kiểm tra điều kiện tiên quyết môn học thông qua Service"""

    def get(self, request, MAHV, MAMH):
        res = DieuKienService.kiem_tra_dieu_kien_hoc_mon(MAHV, MAMH)
        return success(MAHV=MAHV, MAMH=MAMH, KQUA=res)
