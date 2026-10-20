# QLGV API — đồng bộ SQL chuẩn, giữ nguyên 8 bảng BRD

Python 3.12+, Django 5.2 LTS, Django REST Framework. Source giữ cấu trúc mỗi bảng một app, tầng services, serializers, APIView; thêm app AI cho hai bảng PHONG và LICHHOC. SQL Server là schema chuẩn; SQLite là môi trường demo/kiểm thử.

**Đọc [docs/MIGRATION.md](docs/MIGRATION.md) trước khi dùng database cũ. Không trỏ code mới thẳng vào db.sqlite3 cũ.** Database cũ trong ZIP có 2 bản ghi vi phạm CHECK SQL; xem [docs/migration_blocked.json](docs/migration_blocked.json). Bản gốc được giữ nguyên.

## Chạy demo ngay (SQLite)

Gói có `db_chuan.sqlite3` riêng, nạp đúng 161 dòng chuẩn. Không tự hợp nhất nó với dữ liệu cũ.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Admin demo: `admin` / `12345678`; tài khoản thường: `user1` / `12345678`. Mật khẩu này chỉ dùng demo. Trang admin `/admin/` chỉ xem BRD; dùng API CRUD để áp dụng validation và khóa nghiệp vụ. Ba model khóa ghép không đăng ký admin vì Django Admin chưa hỗ trợ CompositePrimaryKey.

Nếu muốn tự tạo database demo MỚI (tên chưa tồn tại):

```powershell
$env:QLGV_DB_PATH = "db_demo_moi.sqlite3"
python manage.py init_schema
python manage.py migrate
python manage.py seed_data
```

`init_schema` dừng khi thấy bảng BRD đã tồn tại. `seed_data` chỉ nạp khi cả 8 bảng trống, không update dữ liệu cũ. Ngày trả theo ISO datetime; MUCLUONG lưu 4 số lẻ; khóa JSON bảng BRD viết hoa theo SQL.

## Thử AI bằng Postman

Chọn Authorization → Basic Auth: admin / 12345678. Không dùng Basic Auth qua HTTP ngoài localhost; khi triển khai dùng HTTPS.

1. `POST /api/phong/`:

```json
{"MAPHONG":"A101","SUCCHUA":60,"LOAI":"LT"}
```

2. `POST /api/ai/xep-lich/`:

```json
{"HOCKY":1,"NAM":2006,"luu":false}
```

Đặt `luu=true` để lưu lịch. Học kỳ/năm phải có trong GIANGDAY; dữ liệu mẫu dùng 2006/2007. CP-SAT không cần API key.

3. Tạo tài khoản học viên trước khi đăng nhập thử. Ví dụ từ shell:

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User
User.objects.create_user(username='K1105', password='DatMatKhauCuaBan')
exit()
```

Admin cấp username bằng MAHV có sẵn; không sửa bảng HOCVIEN để thêm liên kết. Chuyển Basic Auth sang học viên, gọi `POST /api/ai/goi-y-dang-ky/`:

```json
{"HOCKY":1,"NAM":2006,"so_thich":{"tin_chi_min":12,"tin_chi_max":20,"thu_tranh":[7],"ca_uu_tien":[1,2],"ma_mon_uu_tien":["THDC"]}}
```

Bộ seed có lịch lớp cố định và nhiều môn tiên quyết; kết quả gợi ý có thể rỗng, đó là kết quả hợp lệ. Muốn thử happy path đăng ký thêm cần phân công khác môn, đủ tiên quyết, không trùng giờ và còn chỗ. Không sửa dữ liệu chuẩn chỉ để ép AI có kết quả.

4. `POST /api/ai/xac-nhan-dang-ky/`:

```json
{"lich_hoc":[3,7]}
```

Thay id bằng kết quả gợi ý thực tế. API kiểm tra lại, không chấp nhận id không tồn tại/trùng/đã đầy/thiếu tiên quyết/trùng giờ. Một lớp lỗi thì rollback toàn lô. Gợi ý không tự lưu đăng ký.

5. Nếu muốn nhập `yeu_cau` tiếng Việt, đặt biến môi trường `ANTHROPIC_API_KEY` và `AI_MODEL` (tên model được cấp cho tài khoản). Không hard-code key. Khi không có LLM, `co_dung_ai=false`; dùng so_thich hoặc giá trị mặc định, câu tiếng Việt không tự được phân tích. `ca_uu_tien` là ưu tiên mềm; `thu_tranh` là điều kiện cứng.

## API dữ liệu

| Method | URL | Quyền / hành vi |
|---|---|---|
| GET | `/api/khoa/`, `/api/giaovien/`, `/api/hocvien/`, `/api/monhoc/` | Giữ endpoint danh sách cũ, JSON tên mới |
| GET | `/api/khoa/KHMT/quy-luong/` | Quỹ lương, tiền dạng chuỗi chính xác 4 số lẻ |
| GET | `/api/hocvien/K1101/diem-tb/` | Điểm TB lấy điểm cao nhất mỗi môn như code cũ |
| GET | `/api/hocvien/K1101/kiem-tra-dieu-kien/CSDL/` | Tất cả tiên quyết |
| GET/POST | `/api/du-lieu/{ten_bang_viet_thuong}/` | Đăng nhập đọc; admin ghi |
| GET/PUT/PATCH/DELETE | `/api/du-lieu/khoa/KHMT/` và các bảng khóa đơn tương tự | Khóa không được sửa |
| GET/PUT/PATCH/DELETE | `/api/du-lieu/dieukien/CSDL/CTRR/` | Khóa MAMH/MAMH_TRUOC |
| GET/PUT/PATCH/DELETE | `/api/du-lieu/giangday/K11/THDC/` | Khóa MALOP/MAMH |
| GET/PUT/PATCH/DELETE | `/api/du-lieu/ketquathi/K1101/CSDL/1/` | Khóa MAHV/MAMH/LANTHI |
| CRUD | `/api/phong/` | Admin |
| GET | `/api/lich-hoc/` | Đăng nhập; không công khai JSON người đăng ký |
| POST | `/api/ai/xep-lich/` | Admin, preview/lưu |
| POST | `/api/ai/goi-y-dang-ky/`, `/api/ai/xac-nhan-dang-ky/` | Học viên liên kết username=MAHV |
| POST | `/api/tro-ly-ai/` | Chatbot Gemini cũ, SDK tùy chọn; không có key trả trạng thái chưa cấu hình |

Khi đã có lịch phát hành, API khóa các thao tác ghi BRD để giữ lịch/đăng ký nhất quán. Các endpoint mới dùng JSON DRF chuẩn; endpoint cũ giữ wrapper status/data. Ví dụ payload kết quả thi:

```json
{"MAHV":"K1105","MAMH":"THDC","LANTHI":1,"NGTHI":"2006-05-20T00:00:00","DIEM":"5.00","KQUA":"Đạt"}
```

## SQL Server và migration

Xem [docs/MIGRATION.md](docs/MIGRATION.md): DDL gốc giữ nguyên, có schema_only.sql, script SQLite → SQLite, management command SQLite → SQL Server dry-run/commit, đối chiếu nội dung và rollback. Không chạy DDL/seed chuẩn lên DB có dữ liệu.

## Tài liệu bàn giao và kiểm thử

- [docs/MAPPING.md](docs/MAPPING.md): toàn bộ tên bảng/trường, khóa, kiểu và thay đổi thành phần.
- [docs/AI_DESIGN.md](docs/AI_DESIGN.md): 10 bảng, quy tắc AI, đánh đổi lưu đăng ký JSON, concurrency.
- [docs/MIGRATION.md](docs/MIGRATION.md): hướng dẫn chuyển dữ liệu và 2 lỗi nguồn thực tế.
- [docs/VALIDATION.md](docs/VALIDATION.md): kết quả kiểm thử và giới hạn môi trường.

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Giữ nguyên thư mục migration lịch sử để truy vết. Cấu hình canonical_migrations ghi nhận state mới, managed=False cho 8 bảng: không chạy lại DDL cũ. `qlgv.py` sinh dự án khác schema được lưu dạng text ở docs/legacy để không chạy nhầm.
