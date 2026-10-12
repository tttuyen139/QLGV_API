from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GiaoVien, HocVien, MonHoc
from .serializers import GiaoVienSerializer, HocVienSerializer, MonHocSerializer
from .services.giao_vu_service import GiaoVuService


class GiaoVienListAPI(APIView):
    """Lấy danh sách giáo viên kèm tiền lương VNĐ"""

    def get(self, request):
        gv = GiaoVien.objects.all()
        serializer = GiaoVienSerializer(gv, many=True)
        return Response({"status": "success", "total": gv.count(), "data": serializer.data}, status=status.HTTP_200_OK)


class HocVienListAPI(APIView):
    """Lấy danh sách 35 học viên"""

    def get(self, request):
        hv = HocVien.objects.all()
        serializer = HocVienSerializer(hv, many=True)
        return Response({"status": "success", "total": hv.count(), "data": serializer.data}, status=status.HTTP_200_OK)


class MonHocListAPI(APIView):
    """Lấy danh sách 13 môn học"""

    def get(self, request):
        mh = MonHoc.objects.all()
        serializer = MonHocSerializer(mh, many=True)
        return Response({"status": "success", "total": mh.count(), "data": serializer.data}, status=status.HTTP_200_OK)


class QuyLuongKhoaAPI(APIView):
    """Tính quỹ lương của Khoa """

    def get(self, request, ma_khoa):
        res = GiaoVuService.tinh_quy_luong_khoa(ma_khoa)
        if not res:
            return Response({"status": "error", "message": "Khoa không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"status": "success", "data": res}, status=status.HTTP_200_OK)


class DiemTrungBinhHocVienAPI(APIView):
    """ính điểm TB tích lũy """

    def get(self, request, ma_hv):
        res = GiaoVuService.tinh_diem_trung_binh_hoc_vien(ma_hv)
        if not res:
            return Response({"status": "error", "message": "Học viên không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"status": "success", "data": res}, status=status.HTTP_200_OK)


class KiemTraDieuKienAPI(APIView):
    """GET: Kiểm tra điều kiện tiên quyết môn học thông qua Service"""

    def get(self, request, ma_hv, ma_mh):
        res = GiaoVuService.kiem_tra_dieu_kien_hoc_mon(ma_hv, ma_mh)
        return Response({"status": "success", "ma_hv": ma_hv, "ma_mh": ma_mh, "ket_qua": res},
                        status=status.HTTP_200_OK)


from .services.ai_service import AIService


class ChatBotAPI(APIView):
    """POST: Chatbot AI hỗ trợ Giáo vụ"""

    def post(self, request):
        cau_hoi = request.data.get('cau_hoi')
        if not cau_hoi:
            return Response({"status": "error", "message": "Vui lòng nhập 'cau_hoi'"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Gọi AI xử lý
        tra_loi = AIService.hoi_dap_giao_vu(cau_hoi)

        return Response({
            "status": "success",
            "cau_hoi": cau_hoi,
            "tra_loi": tra_loi
        }, status=status.HTTP_200_OK)
