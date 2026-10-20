# Bảng đối chiếu mã nguồn → SQL chuẩn

Nguồn ưu tiên: `QLGV_SQL_Server.sql` đính kèm (prompt gọi là `QLGV_SQL_Server(1).sql`). DDL chuẩn được sao chép nguyên trạng vào docs; không sửa 8 bảng BRD.

## Bảng và thành phần

| Thành phần cũ | Thành phần sau đồng bộ | Xử lý |
|---|---|---|
| `KHOA.Khoa` / `KHOA` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `GIAOVIEN.GiaoVien` / `GIAOVIEN` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `MONHOC.MonHoc` / `MONHOC` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `DIEUKIEN.DieuKien` / `DIEUKIEN` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `LOP.Lop` / `LOP` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `HOCVIEN.HocVien` / `HOCVIEN` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `GIANGDAY.GiangDay` / `GIANGDAY` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `KETQUATHI.KetQuaThi` / `KETQUATHI` | Giữ nguyên | Mỗi bảng vẫn là một app, service/view/serializer riêng |
| `app_quan_ly` | Giữ nguyên | Thành phần dùng chung, seed, migration và validation |
| `qlgv.py` tạo project 9 bảng khác | `docs/legacy/qlgv.py.txt` | Lưu tham khảo, không còn là script chạy được; không tạo nhầm schema |
| `SinhVien`, `GiangVien` trong tài liệu AI | `HOCVIEN.HocVien`, `GIAOVIEN.GiaoVien` | Không tạo bảng đồng nghĩa |
| `LopHocPhan` | Cặp `GIANGDAY(MALOP,MAMH)` + `LICHHOC` | GIANGDAY giữ nguyên khóa ghép và mọi cột |
| `mon_tien_quyet` tự trỏ | `DIEUKIEN(MAMH,MAMH_TRUOC)` | Bắt buộc đạt TẤT CẢ môn trước |
| `so_tin_chi` | `MONHOC.TCLT + MONHOC.TCTH` | Không thêm cột vào MONHOC |
| `DangKyHocPhan` | `LICHHOC.DANGKY` | Danh sách MAHV JSON; chỉ service xác nhận được ghi |
| `Phong` | `PHONG` | Bảng mới 9 |
| `thu`, `ca`, `phong` trên LopHocPhan | `LICHHOC.THU`, `CA`, `MAPHONG` | Bảng mới 10, không ALTER GIANGDAY |
| `sinh_vien.nguoi_dung` | Tài khoản Django có `username = MAHV` | Admin cấp username; API không nhận MAHV client để mạo danh |

## Đối chiếu từng cột

Tên thuộc tính Python và khóa JSON dữ liệu BRD đều đổi sang tên SQL viết hoa. Thuộc tính FK nội bộ Django vẫn có hậu tố `_id`, nhưng `db_column` loại bỏ hậu tố này ở cột vật lý.

### KHOA

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_khoa` | `ma_khoa` | `MAKHOA` | `MAKHOA` | VARCHAR(4); NOT NULL |
| `ten_khoa` | `ten_khoa` | `TENKHOA` | `TENKHOA` | NVARCHAR(40); NOT NULL |
| `ngay_thanh_lap` | `ngay_thanh_lap` | `NGTLAP` | `NGTLAP` | SMALLDATETIME; NOT NULL |
| `truong_khoa` | `truong_khoa_id` | `TRGKHOA` | `TRGKHOA` | FK → GIAOVIEN; NULL |

### GIAOVIEN

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_gv` | `ma_gv` | `MAGV` | `MAGV` | CHAR(4); NOT NULL |
| `ho_ten` | `ho_ten` | `HOTEN` | `HOTEN` | NVARCHAR(40); NOT NULL |
| `hoc_vi` | `hoc_vi` | `HOCVI` | `HOCVI` | NVARCHAR(10); NOT NULL |
| `hoc_ham` | `hoc_ham` | `HOCHAM` | `HOCHAM` | NVARCHAR(10); NULL |
| `gioi_tinh` | `gioi_tinh` | `GIOITINH` | `GIOITINH` | NVARCHAR(3); NOT NULL |
| `ngay_sinh` | `ngay_sinh` | `NGSINH` | `NGSINH` | SMALLDATETIME; NOT NULL |
| `ngay_vao_lam` | `ngay_vao_lam` | `NGVL` | `NGVL` | SMALLDATETIME; NOT NULL |
| `he_so` | `he_so` | `HESO` | `HESO` | NUMERIC(4, 2); NOT NULL |
| `muc_luong` | `muc_luong` | `MUCLUONG` | `MUCLUONG` | MONEY (19,4) / VNĐ; NOT NULL |
| `ma_khoa` | `ma_khoa_id` | `MAKHOA` | `MAKHOA` | FK → KHOA; NOT NULL |

### MONHOC

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_mh` | `ma_mh` | `MAMH` | `MAMH` | VARCHAR(10); NOT NULL |
| `ten_mh` | `ten_mh` | `TENMH` | `TENMH` | NVARCHAR(40); NOT NULL |
| `tin_chi_lt` | `tin_chi_lt` | `TCLT` | `TCLT` | TINYINT; NOT NULL |
| `tin_chi_th` | `tin_chi_th` | `TCTH` | `TCTH` | TINYINT; NOT NULL |
| `ma_khoa` | `ma_khoa_id` | `MAKHOA` | `MAKHOA` | FK → KHOA; NOT NULL |

### DIEUKIEN

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_mh` | `ma_mh_id` | `MAMH` | `MAMH` | FK → MONHOC; NOT NULL |
| `ma_mh_truoc` | `ma_mh_truoc_id` | `MAMH_TRUOC` | `MAMH_TRUOC` | FK → MONHOC; NOT NULL |
| `id` + unique_together | `id` tự tăng | `pk = CompositePrimaryKey(...)` | Khóa ghép `MAMH, MAMH_TRUOC` | Không thêm cột `pk`; old id lưu ở báo cáo migration |

### LOP

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_lop` | `ma_lop` | `MALOP` | `MALOP` | CHAR(3); NOT NULL |
| `ten_lop` | `ten_lop` | `TENLOP` | `TENLOP` | NVARCHAR(40); NOT NULL |
| `truong_lop (đã xóa trong migration cũ)` | `không tồn tại trong DB ZIP` | `TRGLOP` | `TRGLOP` | FK → HOCVIEN; NULL |
| `si_so` | `si_so` | `SISO` | `SISO` | TINYINT; NOT NULL |
| `ma_gvcn` | `ma_gvcn_id` | `MAGVCN` | `MAGVCN` | FK → GIAOVIEN; NOT NULL |

### HOCVIEN

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_hv` | `ma_hv` | `MAHV` | `MAHV` | CHAR(5); NOT NULL |
| `ho` | `ho` | `HO` | `HO` | NVARCHAR(40); NOT NULL |
| `ten` | `ten` | `TEN` | `TEN` | NVARCHAR(10); NOT NULL |
| `ngay_sinh` | `ngay_sinh` | `NGSINH` | `NGSINH` | SMALLDATETIME; NOT NULL |
| `gioi_tinh` | `gioi_tinh` | `GIOITINH` | `GIOITINH` | NVARCHAR(3); NOT NULL |
| `noi_sinh` | `noi_sinh` | `NOISINH` | `NOISINH` | NVARCHAR(40); NOT NULL |
| `ma_lop` | `ma_lop_id` | `MALOP` | `MALOP` | FK → LOP; NOT NULL |

### GIANGDAY

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_lop` | `ma_lop_id` | `MALOP` | `MALOP` | FK → LOP; NOT NULL |
| `ma_mh` | `ma_mh_id` | `MAMH` | `MAMH` | FK → MONHOC; NOT NULL |
| `ma_gv` | `ma_gv_id` | `MAGV` | `MAGV` | FK → GIAOVIEN; NOT NULL |
| `hoc_ky` | `hoc_ky` | `HOCKY` | `HOCKY` | TINYINT; NOT NULL |
| `nam` | `nam` | `NAM` | `NAM` | SMALLINT; NOT NULL |
| `tu_ngay` | `tu_ngay` | `TUNGAY` | `TUNGAY` | SMALLDATETIME; NOT NULL |
| `den_ngay` | `den_ngay` | `DENNGAY` | `DENNGAY` | SMALLDATETIME; NOT NULL |
| `id` + unique_together | `id` tự tăng | `pk = CompositePrimaryKey(...)` | Khóa ghép `MALOP, MAMH` | Không thêm cột `pk`; old id lưu ở báo cáo migration |

### KETQUATHI

| Thuộc tính Python cũ | Cột DB cũ | Thuộc tính/JSON mới | Cột SQL mới | Kiểu SQL / NULL |
|---|---|---|---|---|
| `ma_hv` | `ma_hv_id` | `MAHV` | `MAHV` | FK → HOCVIEN; NOT NULL |
| `ma_mh` | `ma_mh_id` | `MAMH` | `MAMH` | FK → MONHOC; NOT NULL |
| `lan_thi` | `lan_thi` | `LANTHI` | `LANTHI` | TINYINT; NOT NULL |
| `ngay_thi` | `ngay_thi` | `NGTHI` | `NGTHI` | SMALLDATETIME; NOT NULL |
| `diem` | `diem` | `DIEM` | `DIEM` | NUMERIC(4, 2); NOT NULL |
| `ket_qua` | `ket_qua` | `KQUA` | `KQUA` | NVARCHAR(10); NOT NULL |
| `id` + unique_together | `id` tự tăng | `pk = CompositePrimaryKey(...)` | Khóa ghép `MAHV, MAMH, LANTHI` | Không thêm cột `pk`; old id lưu ở báo cáo migration |

## Khác biệt dữ liệu và quy tắc

- Khôi phục `LOP.TRGLOP`: bộ seed chuẩn có đúng 3 lớp trưởng; migration dữ liệu cũ không còn giá trị này thì để NULL, không suy đoán.
- `CASCADE`/`SET_NULL` đổi thành `PROTECT`, phù hợp FK SQL không khai báo ON DELETE CASCADE.
- Ngày cũ DateField trở thành SMALLDATETIME: giữ ngày tại 00:00:00 khi nguồn chỉ có ngày. Không tự cắt giây hoặc bỏ múi giờ.
- MUCLUONG giữ 4 số lẻ MONEY. Tổng quỹ lương trả chuỗi 4 số lẻ để không mất chính xác; giá trị hiển thị VNĐ là trường phụ.
- Kết quả đạt theo SQL: DIEM >= 5; không dùng ngưỡng 4 của tài liệu AI.
- Trưởng khoa khác khoa và ngày thi trước ngày kết thúc môn có trong seed được giữ nguyên vì SQL không cấm.
- `GIANGDAY` chỉ có khóa (MALOP,MAMH): không tự thêm học kỳ/năm vào khóa, không tạo nhiều lần mở cùng môn cho cùng lớp trái schema.
- Python dùng SmallDateTimeField/MoneyField/SQLTinyIntField/SQLCharField/SQLVarCharField để mô tả kiểu SQL. 8 model managed=False: SQL, không phải migration ORM, sở hữu DDL chính xác.
