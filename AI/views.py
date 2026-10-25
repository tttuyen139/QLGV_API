from django.db import transaction, OperationalError
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from HOCVIEN.models import HocVien
from MONHOC.models import MonHoc
from .models import Phong, LichHoc
from .serializers import PhongSerializer, LichHocSerializer, KySerializer, SoThichSerializer
from . import services
from .tro_ly import phan_tich_yeu_cau, giai_thich


def _hv(user):
    # Admin cấp tài khoản có username = MAHV, không cho client tự nhận mã người khác.
    hv = HocVien.objects.filter(pk=user.username).first()
    if hv is None:
        raise PermissionDenied('Tài khoản phải được quản trị viên liên kết bằng username = MAHV.')
    return hv


class PhongViewSet(viewsets.ModelViewSet):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO - DANH MỤC CƠ SỞ VẬT CHẤT
    Chức năng: Quản lý danh sách phòng học lý thuyết và thực hành, kiểm soát sức chứa.
    """
    def get_view_name(self):
        return "Danh Mục Phòng Học"

    queryset = Phong.objects.all()
    serializer_class = PhongSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            services._lock()
            return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                services._lock()
                return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            raise ValidationError('Phòng đang có lịch học, không thể xóa.')


class LichHocViewSet(viewsets.ReadOnlyModelViewSet):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO - THỜI KHÓA BIỂU
    Chức năng: Tra cứu danh mục lịch học và thời khóa biểu các lớp học phần.
    """
    def get_view_name(self):
        return "Thời Khóa Biểu Học Phần"

    serializer_class = LichHocSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = LichHoc.objects.all()
        if self.request.user.is_staff:
            return qs
        _hv(self.request.user)
        return qs  # Chỉ danh mục lịch, không trả JSON DANGKY của người khác.


class AIXepLichView(APIView):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO - PHÒNG GIÁO VỤ
    Chức năng: Tự động sắp xếp thời khóa biểu và phân bổ phòng học theo thuật toán tối ưu ràng buộc.
    """
    def get_view_name(self):
        # Tiêu đề hiển thị trên giao diện Django
        return "Lập Thời Khóa Biểu Tự Động"

    permission_classes = [IsAdminUser]

    def post(self, request):
        s = KySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            return Response(services.xep_lich(**s.validated_data))
        except OperationalError:
            return Response({'detail': 'Dữ liệu đang được cập nhật; vui lòng thử lại.'}, status=409)


class AIGoiYDangKyView(APIView):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO - CỔNG THÔNG TIN SINH VIÊN
    Chức năng: Đề xuất tổ hợp học phần tối ưu theo nhu cầu tín chỉ và nguyện vọng của sinh viên.
    """
    def get_view_name(self):
        # Tiêu đề hiển thị trên giao diện Django (Khớp với URL de-xuat-hoc-phan)
        return "Đề Xuất Lộ Trình Học Phần"

    permission_classes = [IsAuthenticated]

    def post(self, request):
        hv = _hv(request.user)
        s = KySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        yeu_cau = request.data.get('yeu_cau', '')
        if not isinstance(yeu_cau, str) or len(yeu_cau) > 2000:
            raise ValidationError('yeu_cau phải là chuỗi tối đa 2000 ký tự.')
        st, co_ai = phan_tich_yeu_cau(yeu_cau, MonHoc.objects.all())
        # Nếu không dùng LLM, client có thể cung cấp sở thích có cấu trúc.
        v = SoThichSerializer(data=request.data.get('so_thich', st))
        v.is_valid(raise_exception=True)
        unknown = set(v.validated_data['ma_mon_uu_tien']) - set(MonHoc.objects.values_list('MAMH', flat=True))
        if unknown:
            raise ValidationError(f'Mã môn ưu tiên không tồn tại: {sorted(unknown)}')
        result = services.goi_y(hv, s.validated_data['HOCKY'], s.validated_data['NAM'], v.validated_data)
        result['giai_thich'] = giai_thich(yeu_cau, result)
        return Response({'so_thich': v.validated_data, 'co_dung_ai': co_ai, **result})


class AIXacNhanDangKyView(APIView):
    """
    HỆ THỐNG QUẢN LÝ ĐÀO TẠO - CỔNG THÔNG TIN SINH VIÊN
    Chức năng: Kiểm tra tính hợp lệ toàn vẹn và xác nhận đăng ký danh sách học phần vào hệ thống.
    """
    def get_view_name(self):
        # Tiêu đề hiển thị trên giao diện Django (Khớp với URL xac-nhan-hoc-phan)
        return "Xác Nhận Đăng Ký Học Phần"

    permission_classes = [IsAuthenticated]

    def post(self, request):
        hv = _hv(request.user)
        field = serializers.ListField(
            child=serializers.IntegerField(min_value=1), min_length=1, max_length=20
        )
        ids = field.run_validation(request.data.get('lich_hoc'))
        if len(ids) != len(set(ids)):
            raise ValidationError('Không được lặp id lịch học.')
        try:
            return Response(services.xac_nhan(hv, ids), status=201)
        except OperationalError:
            return Response({'detail': 'Dữ liệu đang được cập nhật; vui lòng thử lại.'}, status=409)