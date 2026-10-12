# QLGV-API-Django

API quản lý giáo vụ (Khoa, Giáo viên, Môn học, Điều kiện, Lớp, Học viên, Giảng dạy, Kết quả thi) viết bằng Django + Django REST Framework.

## Cài đặt & chạy

```bash
pip install -r requirements.txt
cp config.example.ini config.ini   # điền GEMINI api_key nếu dùng Trợ lý AI
python manage.py migrate
python manage.py seed_data         # nạp dữ liệu mẫu + tài khoản admin / user1 (mật khẩu 12345678)
python manage.py runserver
```

- Trang quản trị: http://127.0.0.1:8000/admin/ (đăng nhập `admin` / `12345678`)
- Chạy test: `python manage.py test app_quan_ly`

## API

| Method | Đường dẫn | Chức năng |
|---|---|---|
| GET | `/api/giaovien/` | Danh sách giáo viên (kèm lương VNĐ) |
| GET | `/api/hocvien/` | Danh sách học viên |
| GET | `/api/monhoc/` | Danh sách môn học |
| GET | `/api/khoa/<ma_khoa>/quy-luong/` | Tổng quỹ lương của khoa |
| GET | `/api/hocvien/<ma_hv>/diem-tb/` | Điểm trung bình + xếp loại |
| GET | `/api/hocvien/<ma_hv>/kiem-tra-dieu-kien/<ma_mh>/` | Kiểm tra môn tiên quyết |
| POST | `/api/tro-ly-ai/` — body `{"cau_hoi": "..."}` | Trợ lý AI (Gemini) |

## Cấu trúc

Mỗi bảng CSDL là một app Django riêng. App nào có API thì tự chứa `models`, `admin`, `serializers`, `services`, `views`, `urls`, `tests` của nó:

| App | Bảng | API / logic |
|---|---|---|
| `KHOA/` | KHOA | quỹ lương khoa |
| `GIAOVIEN/` | GIAOVIEN | danh sách giáo viên |
| `MONHOC/` | MONHOC | danh sách môn học |
| `DIEUKIEN/` | DIEUKIEN | kiểm tra môn tiên quyết |
| `LOP/` | LOP | (chỉ model + admin) |
| `HOCVIEN/` | HOCVIEN | danh sách học viên |
| `GIANGDAY/` | GIANGDAY | (chỉ model + admin) |
| `KETQUATHI/` | KETQUATHI | điểm trung bình học viên |
| `app_quan_ly/` | — | phần dùng chung: `responses.py` (success/error, BaseListAPI), `utils.py` (format_vnd), Trợ lý AI, lệnh `seed_data` |

`qlgv_project/urls.py` gom `urls.py` của từng app.

> Lưu ý khi cập nhật code: lần tách app này chỉ có migration "chuyển state", không tạo/xóa bảng. CSDL cũ chỉ cần chạy `python manage.py migrate`, dữ liệu được giữ nguyên.
