from rest_framework.views import APIView

from app_quan_ly.responses import success
from .services import DieuKienService


class KiemTraDieuKienAPI(APIView):
    """GET: Kiểm tra điều kiện tiên quyết môn học thông qua Service"""

    def get(self, request, ma_hv, ma_mh):
        res = DieuKienService.kiem_tra_dieu_kien_hoc_mon(ma_hv, ma_mh)
        return success(ma_hv=ma_hv, ma_mh=ma_mh, ket_qua=res)
