from django.urls import path
from app_quan_ly.core_api import CoreAPI

urlpatterns = []

from KHOA.models import Khoa
from KHOA.serializers import KhoaSerializer


class KhoaCRUD(CoreAPI):
    model = Khoa
    serializer_class = KhoaSerializer
    keys = ['MAKHOA']


urlpatterns += [
    path('api/du-lieu/khoa/', KhoaCRUD.as_view()),
    path('api/du-lieu/khoa/<str:MAKHOA>/', KhoaCRUD.as_view()),
]

from GIAOVIEN.models import GiaoVien
from GIAOVIEN.serializers import GiaoVienSerializer


class GiaoVienCRUD(CoreAPI):
    model = GiaoVien
    serializer_class = GiaoVienSerializer
    keys = ['MAGV']


urlpatterns += [
    path('api/du-lieu/giaovien/', GiaoVienCRUD.as_view()),
    path('api/du-lieu/giaovien/<str:MAGV>/', GiaoVienCRUD.as_view()),
]

from MONHOC.models import MonHoc
from MONHOC.serializers import MonHocSerializer


class MonHocCRUD(CoreAPI):
    model = MonHoc
    serializer_class = MonHocSerializer
    keys = ['MAMH']


urlpatterns += [
    path('api/du-lieu/monhoc/', MonHocCRUD.as_view()),
    path('api/du-lieu/monhoc/<str:MAMH>/', MonHocCRUD.as_view()),
]

from DIEUKIEN.models import DieuKien
from DIEUKIEN.serializers import DieuKienSerializer


class DieuKienCRUD(CoreAPI):
    model = DieuKien
    serializer_class = DieuKienSerializer
    keys = ['MAMH', 'MAMH_TRUOC']


urlpatterns += [
    path('api/du-lieu/dieukien/', DieuKienCRUD.as_view()),
    path('api/du-lieu/dieukien/<str:MAMH>/<str:MAMH_TRUOC>/', DieuKienCRUD.as_view()),
]

from LOP.models import Lop
from LOP.serializers import LopSerializer


class LopCRUD(CoreAPI):
    model = Lop
    serializer_class = LopSerializer
    keys = ['MALOP']


urlpatterns += [
    path('api/du-lieu/lop/', LopCRUD.as_view()),
    path('api/du-lieu/lop/<str:MALOP>/', LopCRUD.as_view()),
]

from HOCVIEN.models import HocVien
from HOCVIEN.serializers import HocVienSerializer


class HocVienCRUD(CoreAPI):
    model = HocVien
    serializer_class = HocVienSerializer
    keys = ['MAHV']


urlpatterns += [
    path('api/du-lieu/hocvien/', HocVienCRUD.as_view()),
    path('api/du-lieu/hocvien/<str:MAHV>/', HocVienCRUD.as_view()),
]

from GIANGDAY.models import GiangDay
from GIANGDAY.serializers import GiangDaySerializer


class GiangDayCRUD(CoreAPI):
    model = GiangDay
    serializer_class = GiangDaySerializer
    keys = ['MALOP', 'MAMH']


urlpatterns += [
    path('api/du-lieu/giangday/', GiangDayCRUD.as_view()),
    path('api/du-lieu/giangday/<str:MALOP>/<str:MAMH>/', GiangDayCRUD.as_view()),
]

from KETQUATHI.models import KetQuaThi
from KETQUATHI.serializers import KetQuaThiSerializer


class KetQuaThiCRUD(CoreAPI):
    model = KetQuaThi
    serializer_class = KetQuaThiSerializer
    keys = ['MAHV', 'MAMH', 'LANTHI']


urlpatterns += [
    path('api/du-lieu/ketquathi/', KetQuaThiCRUD.as_view()),
    path('api/du-lieu/ketquathi/<str:MAHV>/<str:MAMH>/<int:LANTHI>/', KetQuaThiCRUD.as_view()),
]
