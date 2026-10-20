import json
import logging

from django.conf import settings

log = logging.getLogger(__name__)

MAC_DINH = {"tin_chi_min": 12, "tin_chi_max": 20, "thu_tranh": [], "ca_uu_tien": [], "ma_mon_uu_tien": []}

CONG_CU = {
    "name": "ghi_nhan_so_thich",
    "description": "Ghi nhận sở thích đăng ký học phần của sinh viên.",
    "input_schema": {
        "type": "object",
        "properties": {
            "tin_chi_min": {"type": "integer", "description": "Số tín chỉ tối thiểu"},
            "tin_chi_max": {"type": "integer", "description": "Số tín chỉ tối đa"},
            "thu_tranh": {
                "type": "array",
                "items": {"type": "integer", "minimum": 2, "maximum": 7},
                "description": "Các thứ muốn tránh (2 = Thứ 2 ... 7 = Thứ 7)",
            },
            "ca_uu_tien": {
                "type": "array",
                "items": {"type": "integer", "minimum": 1, "maximum": 4},
                "description": "Ca muốn học: 1, 2 = buổi sáng; 3, 4 = buổi chiều",
            },
            "ma_mon_uu_tien": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Mã môn muốn ưu tiên, chỉ chọn từ danh sách được cung cấp",
            },
        },
        "required": ["tin_chi_min", "tin_chi_max", "thu_tranh", "ca_uu_tien", "ma_mon_uu_tien"],
    },
}


def _client():
    if not settings.ANTHROPIC_API_KEY or not settings.AI_MODEL:
        return None
    import anthropic

    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=15, max_retries=0)


def phan_tich_yeu_cau(yeu_cau, ds_mon):
    """Trả về (sở thích, có dùng AI hay không)."""
    client = _client()
    if client is None or not yeu_cau:
        return {**MAC_DINH, "thu_tranh": [], "ca_uu_tien": [], "ma_mon_uu_tien": []}, False
    danh_sach = "\n".join(f"- {m.MAMH}: {m.TENMH}" for m in ds_mon)
    try:
        resp = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=500,
            system=(
                "Bạn là trợ lý đăng ký học phần. Trích xuất sở thích của sinh viên. "
                "Trường nào sinh viên không nhắc đến thì dùng mặc định: "
                "tin_chi_min=12, tin_chi_max=20, các danh sách để rỗng."
            ),
            tools=[CONG_CU],
            tool_choice={"type": "tool", "name": "ghi_nhan_so_thich"},
            messages=[
                {
                    "role": "user",
                    "content": f"Các môn mở trong kỳ:\n{danh_sach}\n\nYêu cầu của sinh viên: {yeu_cau}",
                }
            ],
        )
        for block in resp.content:
            if block.type == "tool_use":
                from .serializers import SoThichSerializer

                validator = SoThichSerializer(data={**MAC_DINH, **block.input})
                validator.is_valid(raise_exception=True)
                return validator.validated_data, True
    except Exception:
        log.exception("Lỗi gọi Claude API")
    return {**MAC_DINH, "thu_tranh": [], "ca_uu_tien": [], "ma_mon_uu_tien": []}, False


def giai_thich(yeu_cau, ket_qua):
    mac_dinh = (
        f"Đề xuất {len(ket_qua['de_xuat'])} lớp học phần, tổng {ket_qua['tong_tin_chi']} "
        f"tín chỉ, không trùng lịch và đã đủ điều kiện tiên quyết. {ket_qua['ghi_chu']}"
    ).strip()
    client = _client()
    if client is None:
        return mac_dinh
    try:
        resp = client.messages.create(
            model=settings.AI_MODEL,
            max_tokens=600,
            system=(
                "Bạn là cố vấn học tập. Giải thích ngắn gọn bằng tiếng Việt (tối đa 5 câu) "
                "vì sao danh sách học phần phù hợp với yêu cầu. Chỉ dựa trên dữ liệu được cung cấp."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Yêu cầu: {yeu_cau}\nKết quả: {json.dumps(ket_qua, ensure_ascii=False)}",
                }
            ],
        )
        return "".join(b.text for b in resp.content if b.type == "text") or mac_dinh
    except Exception:
        log.exception("Lỗi gọi Claude API")
        return mac_dinh
