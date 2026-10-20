from app_quan_ly.responses import BaseListAPI
from .models import GiaoVien
from .serializers import GiaoVienSerializer


class GiaoVienListAPI(BaseListAPI):
    """Lấy danh sách giáo viên kèm tiền lương VNĐ"""
    queryset = GiaoVien.objects.select_related('MAKHOA')
    serializer_class = GiaoVienSerializer
