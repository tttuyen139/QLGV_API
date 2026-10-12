from app_quan_ly.responses import BaseListAPI
from .models import GiaoVien
from .serializers import GiaoVienSerializer


class GiaoVienListAPI(BaseListAPI):
    """Lấy danh sách giáo viên kèm tiền lương VNĐ"""
    queryset = GiaoVien.objects.select_related('ma_khoa')
    serializer_class = GiaoVienSerializer
