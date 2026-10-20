from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CoreAPI(APIView):
    model = None
    serializer_class = None
    keys = None
    permission_classes = [IsAuthenticated]

    def _query(self, kwargs):
        return {k: kwargs[k] for k in self.keys}

    def get(self, request, **kwargs):
        if kwargs:
            return Response(self.serializer_class(get_object_or_404(self.model, **self._query(kwargs))).data)
        return Response(self.serializer_class(self.model.objects.all(), many=True).data)

    def _save(self, request, kwargs, partial=False):
        if not request.user.is_staff:
            raise PermissionDenied('Chỉ quản trị viên được thay đổi dữ liệu.')
        obj = get_object_or_404(self.model, **self._query(kwargs)) if kwargs else None
        s = self.serializer_class(obj, data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        # Không thay đổi phân công/lớp/sinh viên/môn khi có lịch đã phát hành.
        # Quản trị viên cần lập kế hoạch phiên bản mới, tránh làm lịch/đăng ký mất hiệu lực.
        from AI.models import LichHoc
        from AI.services import _lock

        try:
            with transaction.atomic():
                _lock()
                if LichHoc.objects.exists():
                    raise ValidationError('Đang có lịch học: khóa sửa BRD để bảo toàn lịch và đăng ký.')
                s.save()
        except IntegrityError:
            raise ValidationError('Dữ liệu vi phạm khóa hoặc ràng buộc SQL.')
        return Response(s.data, status=200 if obj else 201)

    def post(self, request, **kwargs):
        if kwargs:
            raise ValidationError('POST chỉ dùng tại URL danh sách.')
        return self._save(request, kwargs)

    def put(self, request, **kwargs):
        if not kwargs:
            raise ValidationError('Cần đủ khóa bản ghi.')
        return self._save(request, kwargs)

    def patch(self, request, **kwargs):
        if not kwargs:
            raise ValidationError('Cần đủ khóa bản ghi.')
        return self._save(request, kwargs, True)

    def delete(self, request, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Chỉ quản trị viên.')
        if not kwargs:
            raise ValidationError('Cần đủ khóa bản ghi.')
        from AI.models import LichHoc
        from AI.services import _lock

        try:
            with transaction.atomic():
                _lock()
                if LichHoc.objects.exists():
                    raise ValidationError('Đang có lịch học, không được xóa BRD.')
                get_object_or_404(self.model, **self._query(kwargs)).delete()
        except (ProtectedError, IntegrityError):
            raise ValidationError('Bản ghi đang được tham chiếu, không thể xóa.')
        return Response(status=204)
