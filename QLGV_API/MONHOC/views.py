from app_quan_ly.responses import BaseListAPI
from .models import MonHoc
from .serializers import MonHocSerializer


class MonHocListAPI(BaseListAPI):
    """Lấy danh sách môn học"""
    queryset = MonHoc.objects.all()
    serializer_class = MonHocSerializer
