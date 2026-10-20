# Hướng dẫn phát triển QLGV

Đọc README.md, docs/MAPPING.md, docs/MIGRATION.md và docs/AI_DESIGN.md trước khi sửa.

- SQL chuẩn tại docs/QLGV_SQL_Server.sql là nguồn sự thật. Không ALTER 8 bảng BRD hoặc đổi PK (đặc biệt khóa ghép).
- Mỗi bảng vẫn có app riêng, giữ 4 spaces, serializers/views/services tách nhau. Thuộc tính BRD và JSON dùng tên SQL viết hoa, db_column tường minh; FK Python có hậu tố _id, cột SQL không có.
- 8 core model managed=False. SQL Server chạy DDL chuẩn, SQLite mới dùng init_schema. Không chạy code mới thẳng trên db.sqlite3 cũ.
- Migrations lịch sử giữ nguyên để truy vết; settings định tuyến canonical_migrations. Không xóa hoặc fake migrations để che sai DDL.
- Chỉ có thêm PHONG và LICHHOC, tổng 10 bảng nghiệp vụ. Không thêm bảng trung gian, không gọi học phí/điểm trên schema tưởng tượng.
- Mọi ghi lịch, đăng ký, sửa phòng dùng services._lock và transaction. Không cho sửa LICHHOC.DANGKY bằng admin/CRUD. Học viên lấy qua username=MAHV do admin cấp.
- AI chỉ đề xuất. Xác nhận recheck đầy đủ và rollback cả lô nếu lỗi. Điểm đạt >=5 theo SQL.
- Không seed vào dữ liệu thật. Dữ liệu ZIP cũ có 2 lỗi SQL; không tự sửa/xóa chúng.
- Chạy python manage.py check; python manage.py makemigrations --check --dry-run; python manage.py test.
- Test runner tạo DDL core trong SQLite test DB riêng. Không sửa db.sqlite3 gốc trong test.
