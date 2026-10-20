# Kết quả kiểm chứng

- `python manage.py check`: không lỗi.
- `python manage.py makemigrations --check --dry-run`: không có thay đổi chưa ghi nhận.
- `python manage.py test`: 31 test PASS trên SQLite test database riêng.
- Đối chiếu từng trường của toàn bộ 161 dòng seed với INSERT và UPDATE trong SQL: khớp tất cả, gồm 4 trưởng khoa và 3 lớp trưởng.
- Số dòng: KHOA 5; GIAOVIEN 15; MONHOC 13; DIEUKIEN 8; LOP 3; HOCVIEN 35; GIANGDAY 16; KETQUATHI 66.
- File SQL gốc trong docs giữ nguyên từng byte so với file được gửi.
- Database cũ db.sqlite3 giữ nguyên SHA-256 so với file nằm trong ZIP đầu vào.
- Migration trên nguồn thực tế: dừng an toàn vì 2 lỗi CHECK, không tạo DB đích dở dang, không sửa nguồn; xuất migration_blocked.json.
- Migration fixture hợp lệ riêng: khớp số dòng/nội dung trước-sau, bảo toàn old-id mapping và FK, không thay đổi nguồn người dùng.
- Management command import_legacy: đã kiểm thử DRY-RUN rollback và --apply commit vào SQLite tạm, đối chiếu từng trường thành công.
- AI: đã kiểm thử preview không ghi; lưu lịch tránh xung đột; thiếu phòng; gợi ý không ghi; mọi tiên quyết và ngưỡng đạt 5; xác nhận thành công, từ chối lặp/unknown id; rollback sau một lớp đã ghi; sĩ số; giảm sức chứa; phân quyền/không mạo danh; validation sở thích và dữ liệu khóa ghép.

## Giới hạn xác minh

Chưa có SQL Server/ODBC server trong môi trường này, chưa chạy migration hay stress test đồng thời trên SQL Server thật. Đã kiểm tra backend mssql-django cài đặt có select_for_update. Anthropic và Gemini chưa gọi thật vì không có API key; nhánh không cấu hình vẫn chạy được. Không khẳng định hai bản ghi cũ đã được sửa/chuyển thành công. Cần quyết định nghiệp vụ đối với dữ liệu sai trước cutover.

Dữ liệu demo chỉ phục vụ chạy thử. Không trộn 161 dòng seed với DB cũ. Những test sửa dữ liệu chỉ chạy trong test database/temp fixture.

## Phiên bản đã chạy

- Django: 5.2.18
- djangorestframework: 3.18.3
- ortools: 9.15.6755
- anthropic: 1.15.0
- mssql-django: 1.8.0
