"""Cổng học viên qua Browsable API; dùng lại nghiệp vụ hiện có."""
from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse as api_reverse
from rest_framework.views import APIView

from AI.models import LichHoc
from AI.serializers import LichHocSerializer, SoThichSerializer
from AI.views import _hv, AIGoiYDangKyView, AIXacNhanDangKyView
from DIEUKIEN.services import DieuKienService
from KETQUATHI.services import KetQuaThiService
from MONHOC.models import MonHoc
from app_quan_ly.views import ChatBotAPI


class RoleLoginView(LoginView):
    template_name = 'rest_framework/login.html'

    def get_success_url(self):
        # Giữ next an toàn do Django kiểm tra, nếu không có thì chọn theo vai trò.
        return self.get_redirect_url() or reverse(
            'admin:index' if self.request.user.is_staff else 'student-dashboard'
        )


@login_required
def entry(request):
    return redirect('admin:index' if request.user.is_staff else 'student-dashboard')


class StudentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def student(self, request):
        return _hv(request.user)


class StudentHome(StudentAPI):
    """Chọn liên kết trong kết quả để sử dụng chức năng. POST có ô nhập JSON ở cuối trang."""
    def get_view_name(self):
        return 'Cổng API học viên'

    def get(self, request):
        hv = self.student(request)
        if request.accepted_renderer.format == 'api':
            return redirect('student-dashboard')
        names = [
            ('Lịch học của tôi', 'student-schedule'),
            ('Danh mục lịch mở đăng ký', 'lich-hoc-list'),
            ('Điểm trung bình của tôi', 'student-average'),
            ('Kiểm tra môn tiên quyết', 'student-prerequisites'),
            ('Gợi ý học phần', 'student-suggest'),
            ('Xác nhận đăng ký', 'student-confirm'),
            ('Trợ lý giáo vụ', 'student-chat'),
        ]
        return Response({
            'hoc_vien': {'MAHV': hv.pk, 'HO_TEN': f'{hv.HO} {hv.TEN}', 'MALOP': hv.MALOP_id},
            'chuc_nang': {label: api_reverse(name, request=request) for label, name in names},
            'huong_dan': 'Nhấn liên kết. Với chức năng POST, mở Raw data, chọn application/json, nhập dữ liệu mẫu và nhấn POST.',
        })


class MySchedule(StudentAPI):
    def get_view_name(self):
        return 'Lịch học của tôi'

    def get(self, request):
        hv = self.student(request)
        # JSON contains không được SQLite hỗ trợ; lọc danh sách đăng ký ở Python.
        ids = [l.pk for l in LichHoc.objects.only('id', 'MALOP_id', 'DANGKY')
               if l.MALOP_id == hv.MALOP_id or hv.pk in l.DANGKY]
        rows = LichHoc.objects.filter(pk__in=ids).order_by('THU', 'CA', 'id')
        return Response({'MAHV': hv.pk, 'total': len(ids),
                         'lich_hoc': LichHocSerializer(rows, many=True).data})


class MyAverage(StudentAPI):
    def get_view_name(self):
        return 'Điểm trung bình của tôi'

    def get(self, request):
        hv = self.student(request)
        return Response(KetQuaThiService.tinh_diem_trung_binh_hoc_vien(hv.pk))


class MyPrerequisites(StudentAPI):
    def get_view_name(self):
        return 'Kiểm tra môn tiên quyết'

    def get(self, request):
        hv = self.student(request)
        mamh = request.query_params.get('MAMH', '').strip()
        if not mamh:
            return Response({
                'huong_dan': 'Thêm ?MAMH=<mã môn> vào đường dẫn, hoặc chọn liên kết của một môn bên dưới.',
                'mon_hoc': [{'MAMH': m.pk, 'TENMH': m.TENMH,
                            'kiem_tra': api_reverse('student-prerequisites', request=request) + '?MAMH=' + quote(m.pk, safe='')}
                           for m in MonHoc.objects.all().order_by('MAMH')],
            })
        if not MonHoc.objects.filter(pk=mamh).exists():
            return Response({'detail': 'Môn học không tồn tại.'}, status=404)
        return Response({'MAHV': hv.pk, 'MAMH': mamh,
                         'KQUA': DieuKienService.kiem_tra_dieu_kien_hoc_mon(hv.pk, mamh)})


class SuggestInput(serializers.Serializer):
    HOCKY = serializers.IntegerField(min_value=1, max_value=3)
    NAM = serializers.IntegerField(min_value=1900, max_value=2079)
    yeu_cau = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    so_thich = SoThichSerializer(required=False)


class ConfirmInput(serializers.Serializer):
    lich_hoc = serializers.ListField(child=serializers.IntegerField(min_value=1),
                                     min_length=1, max_length=20)


class ChatInput(serializers.Serializer):
    cau_hoi = serializers.CharField(max_length=2000)


class StudentAction(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        _hv(request.user)


class StudentSuggest(StudentAction):
    """GET chỉ hướng dẫn; gửi POST để tạo gợi ý, chưa lưu đăng ký. Dùng học kỳ/năm có trong dữ liệu phân công."""
    serializer_class = SuggestInput

    def get_view_name(self):
        return 'Gợi ý học phần'

    def get(self, request):
        from GIANGDAY.models import GiangDay
        return Response({'huong_dan': 'Sửa học kỳ/năm theo danh sách; gửi JSON bằng POST.',
                         'hoc_ky_hien_co': list(GiangDay.objects.values('HOCKY', 'NAM').distinct().order_by('NAM', 'HOCKY')),
                         'mau_json': {'HOCKY': 1, 'NAM': 2006, 'so_thich': {'tin_chi_min': 0, 'tin_chi_max': 20}}})

    def post(self, request):
        return AIGoiYDangKyView.post(self, request)


class StudentConfirm(StudentAction):
    """Lấy id thực tế từ danh mục lịch hoặc kết quả gợi ý; POST mới ghi đăng ký."""
    serializer_class = ConfirmInput

    def get_view_name(self):
        return 'Xác nhận đăng ký học phần'

    def get(self, request):
        return Response({'huong_dan': 'Gửi lich_hoc là mảng 1–20 id lịch thực tế, không lặp. Ví dụ dưới đây chỉ minh họa; thay id trước khi gửi.',
                         'mau_json': {'lich_hoc': [1]},
                         'danh_muc_lich': api_reverse('lich-hoc-list', request=request)})

    def post(self, request):
        return AIXacNhanDangKyView.post(self, request)


class StudentChat(StudentAction):
    serializer_class = ChatInput

    def get_view_name(self):
        return 'Trợ lý giáo vụ'

    def get(self, request):
        return Response({'huong_dan': 'Gửi câu hỏi bằng POST; cần cấu hình Gemini để nhận trả lời từ dịch vụ AI.',
                         'mau_json': {'cau_hoi': 'Trường hiện có những khoa nào?'}})

    def post(self, request):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        return ChatBotAPI.post(self, request)


class MyClass(StudentAPI):
    def get_view_name(self):
        return 'Lớp của tôi'

    def get(self, request):
        from LOP.serializers import LopSerializer
        hv = self.student(request)
        return Response(LopSerializer(hv.MALOP).data)


class MyResults(StudentAPI):
    def get_view_name(self):
        return 'Kết quả thi của tôi'

    def get(self, request):
        from KETQUATHI.models import KetQuaThi
        from KETQUATHI.serializers import KetQuaThiSerializer
        hv = self.student(request)
        rows = KetQuaThi.objects.filter(MAHV=hv).select_related('MAMH').order_by('MAMH_id', 'LANTHI')
        data = [{**KetQuaThiSerializer(row).data, 'TENMH': row.MAMH.TENMH} for row in rows]
        return Response({'MAHV': hv.pk, 'total': len(data), 'ket_qua_thi': data})


class CourseCatalog(StudentAPI):
    def get_view_name(self):
        return 'Danh mục học phần'

    def get(self, request):
        from AI import services
        hv = self.student(request)
        gd = services._ds_gd()
        rows = []
        for l in LichHoc.objects.select_related('MAMH', 'MAPHONG').order_by('THU', 'CA', 'id'):
            g = gd.get((l.MALOP_id, l.MAMH_id))
            if g is None:
                continue
            siso = services._si_so(l, g)
            rows.append({**LichHocSerializer(l).data, 'TENMH': l.MAMH.TENMH,
                         'HOCKY': g.HOCKY, 'NAM': g.NAM,
                         'TINCHI': l.MAMH.TCLT + l.MAMH.TCTH,
                         'CHO_TRONG': max(0, min(l.SISO_TOIDA, l.MAPHONG.SUCCHUA) - siso),
                         'DA_CO_LICH': l.MALOP_id == hv.MALOP_id or hv.pk in l.DANGKY})
        return Response({'total': len(rows), 'hoc_phan': rows})



from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import PermissionDenied


@login_required
@ensure_csrf_cookie
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin:index')
    try:
        hv = _hv(request.user)
    except PermissionDenied:
        return render(request, 'student/dashboard.html', {'unlinked': True}, status=403)
    return render(request, 'student/dashboard.html', {'hv': hv})
