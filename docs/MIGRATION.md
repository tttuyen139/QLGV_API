# Phương án migration bảo toàn dữ liệu

## Kết quả kiểm tra file ZIP thực tế

`db.sqlite3` có 1 dòng mỗi bảng, tổng 8 dòng nghiệp vụ; khác bộ seed SQL 161 dòng. Giữ nguyên file gốc trong gói bàn giao, không tự nạp seed lên dữ liệu này.

Có 2 bản ghi không đạt ràng buộc SQL:

| Bảng | Khóa/giá trị | Vi phạm | Hướng xử lý cần quyết định |
|---|---|---|---|
| DIEUKIEN | PY1 → PY1 | CK_DK_KHACMON: môn không được là tiên quyết của chính nó | Xác định môn trước đúng từ nghiệp vụ; không đoán mã, không tự xóa dòng |
| KETQUATHI | MAHV=123, MAMH=PY1, LANTHI=1; DIEM=8, KQUA=Pass | CK_KQT_KQUA yêu cầu Đạt khi DIEM>=5 | Đề xuất đổi Pass thành Đạt sau khi đối chiếu ý nghĩa với chủ dữ liệu |

`migration_blocked.json` chứa lý do, dữ liệu được chuyển tên và old-id mapping. Chưa tạo database đích chứa dữ liệu cũ; không thể đồng thời giữ nguyên hai giá trị sai và thỏa CHECK SQL. Không tắt constraint, không bỏ dòng lỗi hoặc chuẩn hóa im lặng.

## A. SQLite → SQLite (đã kiểm thử)

1. Dừng runserver, job, mọi tiến trình đang ghi DB. Giữ bản ZIP gốc. Script dùng SQLite backup API, lấy snapshot nhất quán gồm cả WAL đã commit.
2. Chọn đường dẫn đích CHƯA tồn tại. Không sửa file nguồn. Từ thư mục có manage.py:

```powershell
python scripts/migrate_legacy_sqlite.py --source db.sqlite3 --target db_chuyen_moi.sqlite3
```

3. Với dữ liệu ZIP hiện tại, lệnh dừng và tạo `db_chuyen_moi.sqlite3.blocked.json`. Mở báo cáo, xác định quy tắc xử lý. Nếu cần sửa, chỉ sửa trên BẢN SAO, lưu nhật ký trước/sau, không đụng bản gốc. Mỗi lần chạy chọn tên đích mới.
4. Khi nguồn hợp lệ: script sao chép toàn bộ DB và bảng tài khoản, rebuild 8 bảng trên bản sao bằng DDL chuyển từ SQL chuẩn; copy từng trường; chỉ bỏ cột kỹ thuật id sau khi lưu ánh xạ id → khóa ghép trong báo cáo.
5. Script kiểm tra CHECK, FK, số lượng, nội dung mọi trường, precision/length/date/tinyint, integrity_check. Lỗi bất kỳ: rollback và xóa file tạm. Không công bố DB đích dở dang. Cột lạ chưa có mapping cũng gây dừng.
6. Chỉ sau thông báo `content_verified: true`, cấu hình và chạy:

```powershell
$env:QLGV_DB_PATH = "db_chuyen_moi.sqlite3"
python manage.py migrate
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

7. Smoke test từng bảng, khóa ghép, quỹ lương, điểm TB; kiểm tra auth cũ và toàn bộ báo cáo. Không chạy seed_data sau migration. Giữ source và báo cáo old-id để audit các liên kết admin log hoặc external id cũ. Lịch sử admin log giữ nguyên chuỗi object_id cũ, tra cứu bằng old-id mapping; không tự rewrite audit log.
8. Rollback: dừng app, quay lại code cũ + db.sqlite3 gốc. Nếu đã cho phép người dùng ghi lên DB mới, phải export/diff các thay đổi mới trước rollback; không bỏ các giao dịch phát sinh.

Mật khẩu băm, user/group/permission và các bảng phụ trong SQLite được giữ nguyên qua backup DB. History migration cũ giữ nguyên, namespace canonical_migrations mới không chạy lại các thao tác DDL lịch sử.

## B. SQLite → SQL Server (có script, chưa chạy SQL Server thật)

1. BACKUP DATABASE nguồn SQL Server nếu có; tạo database staging mới riêng, ví dụ QLGV_MIG. Không chạy script tạo DB chuẩn có seed lên DB đang chứa dữ liệu. Chọn QLGV_MIG trong SSMS rồi chạy `docs/schema_only.sql`: 8 bảng, kiểu, khóa và CHECK lấy nguyên DDL chuẩn, chưa có dữ liệu.
2. Cài ODBC Driver 18 của Microsoft trên Windows; `pip install -r requirements-sqlserver.txt`. Cấu hình biến môi trường:

```powershell
$env:QLGV_DB_ENGINE = "mssql"
$env:DB_NAME = "QLGV_MIG"
$env:DB_HOST = "localhost"
$env:DB_USER = "tai_khoan_sql"
$env:DB_PASSWORD = "mat_khau_cua_ban"
python manage.py migrate
python manage.py import_legacy --source db.sqlite3
```

3. Lệnh mặc định DRY-RUN: preflight CHECK/FK trên snapshot, khóa bảng đích, yêu cầu cả 8 bảng trống, insert rồi đối chiếu từng trường và rollback. Với nguồn hiện tại, preflight sẽ dừng do lỗi dữ liệu nêu trên. Nếu dry-run thành công, chạy `python manage.py import_legacy --source BAN_SAO_DA_DOI_CHIEU.sqlite3 --apply` để commit. Trưởng khoa/lớp trưởng gán sau khi nạp các bảng cha/con để xử lý vòng FK.
4. Tài khoản và quyền hệ thống không trộn tự động sang SQL Server. Trước khi chuyển môi trường, từ CODE CŨ + DB CŨ export riêng `auth.User`, `auth.Group` với `dumpdata --natural-foreign --natural-primary`; đích mới đã migrate thì kiểm tra username/group/permission codename rồi loaddata. Không copy session đăng nhập giữa môi trường. Nếu đích có user trùng thì dừng để mapping rõ ràng. Tạo superuser mới cho staging nếu chỉ smoke test.
5. So sánh report old-id, 8 COUNT, dữ liệu từng trường, tiền 4 số lẻ, Unicode, CHECK/FK, API, tài khoản/quyền; backup staging sau nghiệm thu. Chuyển kết nối vào khung giờ dừng ghi. Giữ nguồn bất biến cho rollback.

Không dùng --fake cho một database chưa được đối chiếu DDL. Không xóa/squash migration lịch sử. 8 bảng dùng managed=False nên Django migrate chỉ quản lý bảng hệ thống và 2 bảng AI, không ALTER BRD.

## Phân biệt schema chuẩn và schema demo

SQL Server là môi trường có đúng CHAR/VARCHAR/NVARCHAR/TINYINT/SMALLDATETIME/MONEY. SQLite dùng để chạy nhanh và kiểm thử; kiểu động, collation và khóa đồng thời khác SQL Server. Không coi kiểm thử SQLite là chứng nhận SQL Server. Cần chạy dry-run và test đồng thời trên SQL Server thật trước sử dụng thực tế.
