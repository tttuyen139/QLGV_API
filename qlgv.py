"""
Chạy:  python tao_project.py
Kết quả: thư mục QuanLyGiaoVu/ và file QuanLyGiaoVu.zip
"""
import shutil
from pathlib import Path

GOC = Path("QuanLyGiaoVu")

FILES = {

# =====================================================================
"README.md": r'''
# ĐỒ ÁN MÔN HỌC – HỆ THỐNG QUẢN LÝ GIÁO VỤ (Web API)

- **Chủ đề:** 2 – Web API / Backend API Server / RESTful API (không cần frontend)
- **Công nghệ:** Python 3.12, Django 5.2 (LTS), Django REST Framework, SQL Server (mssql-django)
- **Kiến trúc:** MVC

---

## 1. Đáp ứng yêu cầu đề bài

| Yêu cầu | Cách đáp ứng |
|---|---|
| CSDL 5–10 bảng | 9 bảng nghiệp vụ (mục 3) |
| Tiếng Việt có dấu, tiền VNĐ | DB collation `Vietnamese_CI_AS`, cột nvarchar; học phí lưu số nguyên VNĐ |
| Tối thiểu 2 đối tượng người dùng | Quản trị viên, Người dùng đã đăng ký (Giảng viên / Sinh viên), Khách |
| API đăng nhập, đăng ký | `/api/auth/dang-ky/`, `/api/auth/dang-nhap/` |
| REST GET/POST/PUT/DELETE | ViewSet của Django REST Framework |
| API chức năng quan trọng | Đăng ký học phần, nhập điểm, tính học phí |
| Kiểm thử bằng Postman | Xem mục 6 |
| Thiết kế OOP / MVC | Mục 2 |

> Lưu ý: Django tự sinh thêm bảng hệ thống (django_migrations, auth_group, authtoken_token...).
> Nên hỏi giảng viên giới hạn 5–10 bảng chỉ tính bảng nghiệp vụ hay tính cả các bảng này.

---

## 2. Mô hình MVC trong Django

Django gọi là MTV (Model–Template–View) nhưng bản chất là MVC. Với Web API:

| MVC | File | Vai trò |
|---|---|---|
| **Model** | `giaovu/models.py` | Định nghĩa bảng, quan hệ, logic dữ liệu |
| **View** (hiển thị) | `giaovu/serializers.py` | Chuyển dữ liệu thành JSON trả cho client |
| **Controller** | `giaovu/views.py`, `giaovu/urls.py`, `giaovu/permissions.py` | Nhận request, phân quyền, xử lý nghiệp vụ, điều hướng |

Ưu điểm: tách biệt các thành phần, dễ quản lý và bảo trì mã nguồn.

---

## 3. Thiết kế CSDL (9 bảng)

| Bảng | Mô tả | Khóa ngoại |
|---|---|---|
| NguoiDung | Tài khoản + vai trò (QT/GV/SV) | – |
| Khoa | Khoa | – |
| Lop | Lớp sinh hoạt | Khoa |
| SinhVien | Hồ sơ sinh viên | NguoiDung (1-1), Lop |
| GiangVien | Hồ sơ giảng viên | NguoiDung (1-1), Khoa |
| MonHoc | Môn học, số tín chỉ, đơn giá tín chỉ (VNĐ) | – |
| LopHocPhan | Lớp học phần theo học kỳ | MonHoc, GiangVien |
| DangKyHocPhan | Sinh viên đăng ký lớp học phần + điểm | SinhVien, LopHocPhan |
| HocPhi | Học phí theo học kỳ (VNĐ) | SinhVien |

Quan hệ: Khoa 1–n Lớp, Khoa 1–n Giảng viên, Lớp 1–n Sinh viên, Môn học 1–n Lớp học phần,
Giảng viên 1–n Lớp học phần, Sinh viên n–n Lớp học phần (qua DangKyHocPhan), Sinh viên 1–n Học phí.

Điểm tổng kết = Điểm quá trình × 0,4 + Điểm thi × 0,6.
Học phí = Σ (số tín chỉ × đơn giá tín chỉ) của các học phần đã đăng ký trong học kỳ.

---

## 4. Đối tượng người dùng

| Đối tượng | Quyền |
|---|---|
| Khách | Xem khoa, lớp, môn học, lớp học phần; đăng ký tài khoản |
| Sinh viên (đã đăng ký) | Đăng ký/hủy học phần, xem bảng điểm và học phí của mình |
| Giảng viên (đã đăng ký) | Xem danh sách đăng ký lớp mình dạy, nhập điểm |
| Quản trị viên | Toàn quyền: quản lý danh mục, hồ sơ, tính học phí |

---

## 5. Cài đặt và chạy

1. Cài **ODBC Driver 18 for SQL Server** (trang Microsoft) và SQL Server.
2. Tạo database: chạy file `tao_database.sql` trong SSMS.
3. Sửa thông tin kết nối trong `quanlygiaovu/settings.py` (USER, PASSWORD, HOST)
   hoặc đặt biến môi trường `DB_USER`, `DB_PASSWORD`, `DB_HOST`.
4. Chạy lệnh:

```bash
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations giaovu
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. Nhập dữ liệu mẫu (tiếng Việt có dấu) tại http://127.0.0.1:8000/admin/
   Ví dụ: "Khoa Công nghệ Thông tin", "Nguyễn Văn An", đơn giá 450000 VNĐ/tín chỉ.

---

## 6. Danh sách API

Gốc: `http://127.0.0.1:8000/api/`

| Phương thức | URL | Quyền | Chức năng |
|---|---|---|---|
| POST | `auth/dang-ky/` | Khách | Đăng ký tài khoản |
| POST | `auth/dang-nhap/` | Khách | Đăng nhập, nhận token |
| GET | `khoa/`, `lop/`, `mon-hoc/`, `lop-hoc-phan/` | Khách | Xem danh mục |
| POST / PUT / DELETE | `khoa/`, `lop/`, `mon-hoc/`, `lop-hoc-phan/` (+ `{id}/`) | Quản trị | Quản lý danh mục |
| GET / POST / PUT / DELETE | `sinh-vien/`, `giang-vien/` (+ `{id}/`) | Quản trị | Quản lý hồ sơ |
| POST | `dang-ky-hoc-phan/` | Sinh viên | Đăng ký học phần (kiểm tra trùng, sĩ số) |
| GET | `dang-ky-hoc-phan/` | SV / GV / QT | Xem đăng ký, bảng điểm |
| DELETE | `dang-ky-hoc-phan/{id}/` | SV / QT | Hủy đăng ký |
| PUT | `dang-ky-hoc-phan/{id}/nhap-diem/` | Giảng viên | Nhập điểm |
| POST | `hoc-phi/tinh-hoc-phi/` | Quản trị | Tính học phí theo tín chỉ |
| GET | `hoc-phi/` | SV / QT | Xem học phí |

**Kiểm thử bằng Postman:**
1. `POST /api/auth/dang-nhap/` với body JSON `{"username": "...", "password": "..."}` → nhận `token`.
2. Các request khác thêm header: `Authorization: Token <token>`.

Ví dụ body:
- Đăng ký học phần: `{"lop_hoc_phan": 1}`
- Nhập điểm: `{"diem_qua_trinh": 8.5, "diem_thi": 7}`
- Tính học phí: `{"ma_sv": "SV001", "hoc_ky": 1, "nam_hoc": "2026-2027"}`

---

## 7. Sản phẩm cần nộp (theo đề)

- [ ] File báo cáo Word + PDF theo mẫu (ERD, sơ đồ lớp, giải thích MVC, danh sách API, ảnh test Postman)
- [ ] Slide thuyết trình
- [ ] Source code (thư mục này)
- [ ] Video thuyết trình ≤ 15 phút, thấy mặt các thành viên (bắt buộc với hệ trực tuyến)
''',

# =====================================================================
"requirements.txt": r'''
Django>=5.2,<5.3
djangorestframework
mssql-django
''',

# =====================================================================
"tao_database.sql": r'''
-- Chạy trong SQL Server Management Studio
CREATE DATABASE QuanLyGiaoVu COLLATE Vietnamese_CI_AS;
GO
''',

# =====================================================================
".gitignore": r'''
venv/
__pycache__/
*.pyc
''',

# =====================================================================
"manage.py": r'''
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quanlygiaovu.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
''',

# =====================================================================
"quanlygiaovu/__init__.py": "",

"quanlygiaovu/settings.py": r'''
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "doi-chuoi-nay-khi-trien-khai-that"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "giaovu",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "quanlygiaovu.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "quanlygiaovu.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": "QuanLyGiaoVu",
        "USER": os.environ.get("DB_USER", "sa"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "MatKhauCuaBan"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": "1433",
        "OPTIONS": {
            "driver": "ODBC Driver 18 for SQL Server",
            "extra_params": "TrustServerCertificate=yes",
        },
    }
}

AUTH_USER_MODEL = "giaovu.NguoiDung"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
''',

"quanlygiaovu/urls.py": r'''
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("giaovu.urls")),
]
''',

"quanlygiaovu/wsgi.py": r'''
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quanlygiaovu.settings")
application = get_wsgi_application()
''',

"quanlygiaovu/asgi.py": r'''
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quanlygiaovu.settings")
application = get_asgi_application()
''',

# =====================================================================
"giaovu/__init__.py": "",
"giaovu/migrations/__init__.py": "",

"giaovu/apps.py": r'''
from django.apps import AppConfig


class GiaovuConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "giaovu"
    verbose_name = "Quản lý giáo vụ"
''',

# ---------------------------------------------------------------- MODEL
"giaovu/models.py": r'''
"""MODEL (MVC): định nghĩa cấu trúc dữ liệu và logic dữ liệu."""
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class NguoiDung(AbstractUser):
    class VaiTro(models.TextChoices):
        QUAN_TRI = "QT", "Quản trị viên"
        GIANG_VIEN = "GV", "Giảng viên"
        SINH_VIEN = "SV", "Sinh viên"

    vai_tro = models.CharField(max_length=2, choices=VaiTro.choices, default=VaiTro.SINH_VIEN)

    @property
    def la_quan_tri(self):
        return self.is_superuser or self.vai_tro == self.VaiTro.QUAN_TRI


class Khoa(models.Model):
    ma_khoa = models.CharField(max_length=10, unique=True)
    ten_khoa = models.CharField(max_length=100)

    def __str__(self):
        return self.ten_khoa


class Lop(models.Model):
    ma_lop = models.CharField(max_length=15, unique=True)
    ten_lop = models.CharField(max_length=100)
    nien_khoa = models.CharField(max_length=20)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name="lop")

    def __str__(self):
        return self.ten_lop


class SinhVien(models.Model):
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE, related_name="sinh_vien")
    ma_sv = models.CharField(max_length=15, unique=True)
    ho_ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField()
    gioi_tinh = models.CharField(max_length=5, choices=[("Nam", "Nam"), ("Nữ", "Nữ")])
    lop = models.ForeignKey(Lop, on_delete=models.PROTECT, related_name="sinh_vien")

    def __str__(self):
        return f"{self.ma_sv} - {self.ho_ten}"


class GiangVien(models.Model):
    nguoi_dung = models.OneToOneField(NguoiDung, on_delete=models.CASCADE, related_name="giang_vien")
    ma_gv = models.CharField(max_length=15, unique=True)
    ho_ten = models.CharField(max_length=100)
    hoc_vi = models.CharField(max_length=30, blank=True)
    khoa = models.ForeignKey(Khoa, on_delete=models.PROTECT, related_name="giang_vien")

    def __str__(self):
        return self.ho_ten


class MonHoc(models.Model):
    ma_mon = models.CharField(max_length=15, unique=True)
    ten_mon = models.CharField(max_length=150)
    so_tin_chi = models.PositiveSmallIntegerField()
    don_gia_tin_chi = models.DecimalField(max_digits=12, decimal_places=0)  # VNĐ

    def __str__(self):
        return self.ten_mon


class LopHocPhan(models.Model):
    ma_lhp = models.CharField(max_length=20, unique=True)
    mon_hoc = models.ForeignKey(MonHoc, on_delete=models.PROTECT, related_name="lop_hoc_phan")
    giang_vien = models.ForeignKey(GiangVien, on_delete=models.PROTECT, related_name="lop_hoc_phan")
    hoc_ky = models.PositiveSmallIntegerField()
    nam_hoc = models.CharField(max_length=9)
    si_so_toi_da = models.PositiveSmallIntegerField(default=60)

    def __str__(self):
        return self.ma_lhp


class DangKyHocPhan(models.Model):
    diem_validator = [MinValueValidator(0), MaxValueValidator(10)]

    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name="dang_ky")
    lop_hoc_phan = models.ForeignKey(LopHocPhan, on_delete=models.CASCADE, related_name="dang_ky")
    ngay_dang_ky = models.DateTimeField(auto_now_add=True)
    diem_qua_trinh = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                         validators=diem_validator)
    diem_thi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                   validators=diem_validator)

    class Meta:
        unique_together = ("sinh_vien", "lop_hoc_phan")

    @property
    def diem_tong_ket(self):
        if self.diem_qua_trinh is None or self.diem_thi is None:
            return None
        return round(float(self.diem_qua_trinh) * 0.4 + float(self.diem_thi) * 0.6, 2)


class HocPhi(models.Model):
    sinh_vien = models.ForeignKey(SinhVien, on_delete=models.CASCADE, related_name="hoc_phi")
    hoc_ky = models.PositiveSmallIntegerField()
    nam_hoc = models.CharField(max_length=9)
    so_tien = models.DecimalField(max_digits=15, decimal_places=0)  # VNĐ
    da_dong = models.BooleanField(default=False)
    ngay_dong = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("sinh_vien", "hoc_ky", "nam_hoc")
''',

# ---------------------------------------------------------------- VIEW
"giaovu/serializers.py": r'''
"""VIEW (MVC): chuyển dữ liệu Model thành JSON trả về client."""
from rest_framework import serializers
from .models import (NguoiDung, Khoa, Lop, SinhVien, GiangVien,
                     MonHoc, LopHocPhan, DangKyHocPhan, HocPhi)


class DangKyTaiKhoanSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = NguoiDung
        fields = ["id", "username", "password", "email", "first_name", "last_name", "vai_tro"]
        read_only_fields = ["vai_tro"]

    def create(self, validated_data):
        # Tài khoản tự đăng ký mặc định là Sinh viên; quản trị viên gắn hồ sơ SinhVien sau
        return NguoiDung.objects.create_user(**validated_data)


class KhoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Khoa
        fields = "__all__"


class LopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lop
        fields = "__all__"


class SinhVienSerializer(serializers.ModelSerializer):
    class Meta:
        model = SinhVien
        fields = "__all__"


class GiangVienSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiangVien
        fields = "__all__"


class MonHocSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonHoc
        fields = "__all__"


class LopHocPhanSerializer(serializers.ModelSerializer):
    ten_mon = serializers.CharField(source="mon_hoc.ten_mon", read_only=True)
    ten_giang_vien = serializers.CharField(source="giang_vien.ho_ten", read_only=True)
    so_da_dang_ky = serializers.IntegerField(source="dang_ky.count", read_only=True)

    class Meta:
        model = LopHocPhan
        fields = "__all__"


class DangKyHocPhanSerializer(serializers.ModelSerializer):
    ten_mon = serializers.CharField(source="lop_hoc_phan.mon_hoc.ten_mon", read_only=True)
    diem_tong_ket = serializers.FloatField(read_only=True)

    class Meta:
        model = DangKyHocPhan
        fields = ["id", "sinh_vien", "lop_hoc_phan", "ten_mon", "ngay_dang_ky",
                  "diem_qua_trinh", "diem_thi", "diem_tong_ket"]
        read_only_fields = ["sinh_vien", "diem_qua_trinh", "diem_thi"]


class NhapDiemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DangKyHocPhan
        fields = ["diem_qua_trinh", "diem_thi"]


class HocPhiSerializer(serializers.ModelSerializer):
    class Meta:
        model = HocPhi
        fields = "__all__"
''',

# ---------------------------------------------------------------- CONTROLLER
"giaovu/permissions.py": r'''
"""CONTROLLER (MVC): phân quyền theo vai trò người dùng."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class LaQuanTri(BasePermission):
    message = "Chỉ quản trị viên được thực hiện thao tác này."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.la_quan_tri


class ChiDocHoacQuanTri(BasePermission):
    """Khách được xem; chỉ quản trị viên được thêm/sửa/xóa."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.la_quan_tri
''',

"giaovu/views.py": r'''
"""CONTROLLER (MVC): nhận request, kiểm tra quyền, xử lý nghiệp vụ."""
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (NguoiDung, Khoa, Lop, SinhVien, GiangVien,
                     MonHoc, LopHocPhan, DangKyHocPhan, HocPhi)
from .permissions import LaQuanTri, ChiDocHoacQuanTri
from .serializers import (DangKyTaiKhoanSerializer, KhoaSerializer, LopSerializer,
                          SinhVienSerializer, GiangVienSerializer, MonHocSerializer,
                          LopHocPhanSerializer, DangKyHocPhanSerializer,
                          NhapDiemSerializer, HocPhiSerializer)

VT = NguoiDung.VaiTro


# ---------- Xác thực ----------
class DangKyTaiKhoanView(generics.CreateAPIView):
    serializer_class = DangKyTaiKhoanSerializer
    permission_classes = [AllowAny]


# ---------- Danh mục: khách xem được, quản trị viên quản lý ----------
class KhoaViewSet(viewsets.ModelViewSet):
    queryset = Khoa.objects.all()
    serializer_class = KhoaSerializer
    permission_classes = [ChiDocHoacQuanTri]


class LopViewSet(viewsets.ModelViewSet):
    queryset = Lop.objects.select_related("khoa")
    serializer_class = LopSerializer
    permission_classes = [ChiDocHoacQuanTri]


class MonHocViewSet(viewsets.ModelViewSet):
    queryset = MonHoc.objects.all()
    serializer_class = MonHocSerializer
    permission_classes = [ChiDocHoacQuanTri]


class LopHocPhanViewSet(viewsets.ModelViewSet):
    queryset = LopHocPhan.objects.select_related("mon_hoc", "giang_vien")
    serializer_class = LopHocPhanSerializer
    permission_classes = [ChiDocHoacQuanTri]


# ---------- Hồ sơ: chỉ quản trị viên ----------
class SinhVienViewSet(viewsets.ModelViewSet):
    queryset = SinhVien.objects.select_related("lop")
    serializer_class = SinhVienSerializer
    permission_classes = [LaQuanTri]


class GiangVienViewSet(viewsets.ModelViewSet):
    queryset = GiangVien.objects.select_related("khoa")
    serializer_class = GiangVienSerializer
    permission_classes = [LaQuanTri]


# ---------- Chức năng chính 1 & 2: Đăng ký học phần, nhập điểm ----------
class DangKyHocPhanViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                           mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = DangKyHocPhanSerializer

    def get_queryset(self):
        u = self.request.user
        qs = DangKyHocPhan.objects.select_related("sinh_vien", "lop_hoc_phan__mon_hoc")
        if u.la_quan_tri:
            return qs
        if u.vai_tro == VT.GIANG_VIEN:
            return qs.filter(lop_hoc_phan__giang_vien__nguoi_dung=u)
        return qs.filter(sinh_vien__nguoi_dung=u)

    def perform_create(self, serializer):
        sv = getattr(self.request.user, "sinh_vien", None)
        if sv is None:
            raise PermissionDenied("Chỉ sinh viên đã có hồ sơ mới được đăng ký học phần.")
        lhp = serializer.validated_data["lop_hoc_phan"]
        if DangKyHocPhan.objects.filter(sinh_vien=sv, lop_hoc_phan=lhp).exists():
            raise ValidationError("Bạn đã đăng ký lớp học phần này.")
        if lhp.dang_ky.count() >= lhp.si_so_toi_da:
            raise ValidationError("Lớp học phần đã đủ sĩ số.")
        serializer.save(sinh_vien=sv)

    @action(detail=True, methods=["put"], url_path="nhap-diem")
    def nhap_diem(self, request, pk=None):
        u = request.user
        if not (u.la_quan_tri or u.vai_tro == VT.GIANG_VIEN):
            raise PermissionDenied("Chỉ giảng viên phụ trách được nhập điểm.")
        dang_ky = self.get_object()  # GV chỉ lấy được bản ghi thuộc lớp mình dạy
        s = NhapDiemSerializer(dang_ky, data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(DangKyHocPhanSerializer(dang_ky).data)


# ---------- Chức năng chính 3: Học phí ----------
class HocPhiViewSet(viewsets.ModelViewSet):
    serializer_class = HocPhiSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [LaQuanTri()]

    def get_queryset(self):
        u = self.request.user
        qs = HocPhi.objects.select_related("sinh_vien")
        return qs if u.la_quan_tri else qs.filter(sinh_vien__nguoi_dung=u)

    @action(detail=False, methods=["post"], url_path="tinh-hoc-phi")
    def tinh_hoc_phi(self, request):
        """Body: {"ma_sv": "SV001", "hoc_ky": 1, "nam_hoc": "2026-2027"}"""
        sv = get_object_or_404(SinhVien, ma_sv=request.data.get("ma_sv"))
        hoc_ky, nam_hoc = request.data.get("hoc_ky"), request.data.get("nam_hoc")

        thanh_tien = ExpressionWrapper(
            F("lop_hoc_phan__mon_hoc__so_tin_chi") * F("lop_hoc_phan__mon_hoc__don_gia_tin_chi"),
            output_field=DecimalField(max_digits=15, decimal_places=0),
        )
        tong = DangKyHocPhan.objects.filter(
            sinh_vien=sv, lop_hoc_phan__hoc_ky=hoc_ky, lop_hoc_phan__nam_hoc=nam_hoc
        ).aggregate(tong=Sum(thanh_tien))["tong"] or 0

        hp, _ = HocPhi.objects.update_or_create(
            sinh_vien=sv, hoc_ky=hoc_ky, nam_hoc=nam_hoc,
            defaults={"so_tien": tong},
        )
        return Response(HocPhiSerializer(hp).data)
''',

"giaovu/urls.py": r'''
"""CONTROLLER (MVC): định tuyến URL đến các xử lý."""
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("khoa", views.KhoaViewSet)
router.register("lop", views.LopViewSet)
router.register("mon-hoc", views.MonHocViewSet)
router.register("lop-hoc-phan", views.LopHocPhanViewSet)
router.register("sinh-vien", views.SinhVienViewSet)
router.register("giang-vien", views.GiangVienViewSet)
router.register("dang-ky-hoc-phan", views.DangKyHocPhanViewSet, basename="dang-ky-hoc-phan")
router.register("hoc-phi", views.HocPhiViewSet, basename="hoc-phi")

urlpatterns = [
    path("auth/dang-ky/", views.DangKyTaiKhoanView.as_view()),
    path("auth/dang-nhap/", obtain_auth_token),
    path("", include(router.urls)),
]
''',

"giaovu/admin.py": r'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (NguoiDung, Khoa, Lop, SinhVien, GiangVien,
                     MonHoc, LopHocPhan, DangKyHocPhan, HocPhi)


@admin.register(NguoiDung)
class NguoiDungAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Vai trò", {"fields": ("vai_tro",)}),)
    list_display = ("username", "email", "vai_tro", "is_staff")


for m in [Khoa, Lop, SinhVien, GiangVien, MonHoc, LopHocPhan, DangKyHocPhan, HocPhi]:
    admin.site.register(m)
''',
}

# =====================================================================
if GOC.exists():
    shutil.rmtree(GOC)

for duong_dan, noi_dung in FILES.items():
    p = GOC / duong_dan
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung.lstrip("\n"), encoding="utf-8")

shutil.make_archive(GOC.name, "zip", root_dir=".", base_dir=GOC.name)
print(f"Đã tạo thư mục {GOC}/ và file {GOC.name}.zip")
