from django.conf import settings

from GIAOVIEN.models import GiaoVien
from KHOA.models import Khoa


class AIService:
    @staticmethod
    def hoi_dap_giao_vu(cau_hoi: str) -> str:
        if not settings.GEMINI_API_KEY:
            return "Trợ lý AI chưa được cấu hình. Vui lòng khai báo GEMINI_API_KEY (xem config.example.ini)."

        try:
            # Import tại đây để project vẫn chạy được khi chưa cài google-generativeai
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)

            # xuất CSDL CONTEXT
            ds_gv = list(GiaoVien.objects.values('ma_gv', 'ho_ten', 'hoc_vi', 'muc_luong', 'ma_khoa_id'))
            ds_khoa = list(Khoa.objects.values('ma_khoa', 'ten_khoa'))

            context = f"""
            Bạn là 'Trợ lý ảo Giáo vụ' của hệ thống QLGV.
            Dưới đây là cơ sở dữ liệu hiện tại của trường:
            - Danh sách Khoa: {ds_khoa}
            - Danh sách Giáo viên (Lương tính bằng VNĐ): {ds_gv}

            Quy tắc:
            1. Trả lời chính xác dựa trên dữ liệu trên.
            2. Trả lời thân thiện, lịch sự bằng tiếng Việt.
            3. Định dạng lương rõ ràng bằng VNĐ (Ví dụ: 2.025.000 VNĐ).
            """

            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(f"{context}\n\nCâu hỏi: {cau_hoi}")

            return response.text.strip()
        except Exception as e:
            return f"Xin lỗi, Trợ lý AI đang bận. Chi tiết lỗi: {str(e)}"
