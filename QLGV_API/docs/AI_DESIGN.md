# AI và giới hạn 10 bảng nghiệp vụ

## Cấu trúc

Giữ nguyên KHOA, MONHOC, DIEUKIEN, GIAOVIEN, LOP, HOCVIEN, GIANGDAY, KETQUATHI. Chỉ thêm:

| Bảng | Cột chính | Vai trò |
|---|---|---|
| PHONG | MAPHONG (PK), SUCCHUA, LOAI | Danh mục phòng |
| LICHHOC | id, MALOP, MAMH, MAPHONG, THU, CA, SISO_TOIDA, DANGKY(JSON) | Một lịch bổ sung cho mỗi cặp khóa GIANGDAY; danh sách MAHV đăng ký ngoài lớp |

Tổng 10 bảng NGHIỆP VỤ. Django còn có các bảng auth/admin/session/migration; không tính chúng là bảng BRD.

Vì giới hạn 2 bảng bổ sung và không được thêm cột vào GIANGDAY, không tạo DANGKYHOCPHAN riêng. `DANGKY` là mảng MAHV có kiểm tra bởi service, không có FK SQL cho từng phần tử JSON. Cặp MALOP/MAMH ở LICHHOC cũng được kiểm tra với GIANGDAY trong service; Django chưa hỗ trợ ForeignKey tới composite PK trong luồng này. Đây là đánh đổi rõ ràng về chuẩn hóa dữ liệu và bảo vệ khi ai đó ghi SQL trực tiếp. Không mở CRUD LICHHOC/JSON; chỉ service ghi. Nếu cần triển khai sản phẩm lớn, cần xin thay đổi giới hạn bảng để chuẩn hóa bảng đăng ký, không tự thay BRD.

Không thêm môn tiên quyết tự trỏ vào MONHOC; đọc đủ DIEUKIEN. Không thêm điểm vào LICHHOC; kết quả thi vẫn ở KETQUATHI.

## Quy tắc chuyển từ tài liệu AI

- LopHocPhan tương ứng phân công GIANGDAY, khóa MALOP/MAMH. Học kỳ 1..3; NAM là năm số nguyên, ví dụ 2006, không dùng chuỗi 2026-2027.
- Học viên thuộc lớp gốc được coi đã có lịch toàn bộ các phân công của lớp. Đăng ký thêm lưu MAHV trong JSON; không đổi HOCVIEN.MALOP.
- Số chỗ dùng: max(LOP.SISO, số hồ sơ thực tế của lớp) + số người đăng ký ngoài lớp. Mặc định SISO_TOIDA lấy sức chứa phòng được gán. Chưa có quy định sức chứa lớp riêng trong SQL; không tự thêm cột đó vào BRD.
- Mỗi phân công học 1 ca/tuần: ca1 tiết1–3, ca2 tiết4–6, ca3 tiết7–9, ca4 tiết10–12; thứ2 đến thứ7. Chỉ cấm trùng khi khoảng TUNGAY/DENNGAY giao nhau, bao gồm hai đầu mút. Không xử lý nhiều buổi/tuần hoặc thời khóa biểu theo ngày lễ trong phạm vi này.
- CP-SAT cấm trùng phòng, giáo viên, lớp gốc và mọi học viên đăng ký; phòng đủ chỗ. Phạt thứ7, ca4, phòng dư nhiều chỗ. Không ép loại phòng LT/TH vì SQL không quy định loại phòng bắt buộc cho từng phân công.
- Gợi ý loại môn đã đạt (>=5), thiếu một trong các tiên quyết, trùng môn trong học kỳ, trùng giờ, đầy chỗ. Ưu tiên môn học lại, mã môn và ca ưu tiên; `thu_tranh` là ràng buộc cứng. `ca_uu_tien` là ưu tiên mềm đúng schema sở thích của tài liệu, không phải cam kết chỉ học ca đó.
- Tín chỉ = TCLT+TCTH; không tạo học phí vì SQL không có đơn giá/học phí.
- Không đủ tín chỉ tối thiểu: thử lại với tối thiểu 0, ghi rõ phương án khả thi trong thời gian, không tự nhận tối ưu khi solver chỉ trả FEASIBLE.
- Gợi ý chỉ đọc. Xác nhận kiểm tra lại từng lớp trong transaction; sai một lớp rollback toàn lô, kể cả lớp đã ghi trước đó.
- Mọi ghi lịch/đăng ký và sửa phòng dùng khóa chung theo thứ tự. Khi có lịch, API tạm khóa sửa 8 bảng BRD để tránh thay đổi giáo viên/ngày/lớp làm lịch mất hiệu lực. Admin chỉ xem. Cần quy trình bảo trì có phiên bản nếu muốn sửa BRD sau khi phát hành lịch.
- SQLite có thể trả database locked khi đồng thời ghi; API AI trả 409 để client thử lại. SQL Server dùng select_for_update của backend mssql-django. Chưa chạy stress test đồng thời SQL Server thật.

## Anthropic và chế độ không có key

ANTHROPIC_API_KEY và AI_MODEL đọc từ môi trường; phải điền tên model được cấp cho tài khoản, không hard-code tên model suy đoán trong tài liệu. Không cần key để dùng CP-SAT.

LLM chỉ trích xuất sở thích bằng tool use và giải thích; output phải qua SoThichSerializer (số tín chỉ 0..40, thứ2..7, ca1..4, mã môn tồn tại). Nếu không có key/model hoặc dịch vụ lỗi, `co_dung_ai=false`; yêu cầu tiếng Việt không được tự diễn giải, dùng `so_thich` có cấu trúc hoặc các giá trị mặc định. Có timeout 15s và không retry SDK. Không gửi danh sách học viên hoặc điểm cá nhân cho Anthropic; chỉ mã/tên môn và kết quả đề xuất cần giải thích. Lời giải thích LLM là tham khảo; chỉ dữ liệu cấu trúc/validator quyết định cho phép ghi.

## Tài khoản

Dùng auth.User sẵn có, không thêm bảng tài khoản nghiệp vụ. Admin tạo username trùng MAHV bằng createsuperuser/admin hoặc shell; không cho tự đăng ký/tự đổi liên kết. Các endpoint AI lấy học viên từ username, bỏ qua MAHV do client gửi. Admin dùng is_staff; yêu cầu BasicAuth hoặc SessionAuth của DRF, SessionAuth phải có CSRF khi ghi.
