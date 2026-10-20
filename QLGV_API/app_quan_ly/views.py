from rest_framework import status
from rest_framework.views import APIView

from .responses import success, error
from .services.ai_service import AIService


class ChatBotAPI(APIView):
    """POST: Chatbot AI hỗ trợ Giáo vụ"""

    def post(self, request):
        cau_hoi = request.data.get('cau_hoi')
        if not cau_hoi:
            return error("Vui lòng nhập 'cau_hoi'", status.HTTP_400_BAD_REQUEST)

        tra_loi = AIService.hoi_dap_giao_vu(cau_hoi)
        return success(cau_hoi=cau_hoi, tra_loi=tra_loi)
