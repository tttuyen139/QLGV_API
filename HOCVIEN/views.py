from app_quan_ly.responses import BaseListAPI
from .models import HocVien
from .serializers import HocVienSerializer


class HocVienListAPI(BaseListAPI):
    """Lấy danh sách học viên"""
    queryset = HocVien.objects.all()
    serializer_class = HocVienSerializer
