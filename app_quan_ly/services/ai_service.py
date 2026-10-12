import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding="utf-8")

GEMINI_API_KEY = config.get("GEMINI_API", "api_key", fallback="").strip()

class AIService:
    @staticmethod
    def hoi_dap_giao_vu(cau_hoi: str) -> str:
        try:
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

            # Gọi  model gemini-2.0-flash
            model = genai.GenerativeModel('gemini-3.8-flash')
            response = model.generate_content(f"{context}\n\nCâu hỏi: {cau_hoi}")

            return response.text.strip()
        except Exception as e:
            return f"Xin lỗi, Trợ lý AI đang bận. Chi tiết lỗi: {str(e)}"