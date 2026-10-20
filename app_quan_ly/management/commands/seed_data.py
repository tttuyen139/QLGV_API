from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from KHOA.models import Khoa
from GIAOVIEN.models import GiaoVien
from MONHOC.models import MonHoc
from DIEUKIEN.models import DieuKien
from LOP.models import Lop
from HOCVIEN.models import HocVien
from GIANGDAY.models import GiangDay
from KETQUATHI.models import KetQuaThi


class Command(BaseCommand):
    help = "Nạp toàn bộ dữ liệu mẫu QLGV (chạy lại nhiều lần vẫn an toàn)"

    def handle(self, *args, **options):
        with transaction.atomic():
            run_seed()


def run_seed():
    from django.core.management.base import CommandError
    if any(m.objects.exists() for m in [Khoa, GiaoVien, MonHoc, DieuKien, Lop, HocVien, GiangDay, KetQuaThi]):
        raise CommandError("Chỉ seed khi cả 8 bảng trống; không ghi đè dữ liệu hiện có.")
    print("🚀 Bắt đầu quá trình nạp 100% dữ liệu QLGV...")

    # 2 tk test.
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', '12345678')
    if not User.objects.filter(username='user1').exists():
        User.objects.create_user('user1', 'user1@example.com', '12345678')
    print("✅ Đã tạo tài khoản test (admin / user1)")

    #Bảng KHOA (5 dòng)
    khoa_data = [
        ('KHMT', 'Khoa học máy tính', '2005-06-07'),
        ('HTTT', 'Hệ thống thông tin', '2005-06-07'),
        ('CNPM', 'Công nghệ phần mềm', '2005-06-07'),
        ('MTT', 'Mạng và truyền thông', '2005-10-20'),
        ('KTMT', 'Kỹ thuật máy tính', '2005-12-20'),
    ]
    for mk, tk, ng in khoa_data:
        Khoa.objects.update_or_create(MAKHOA=mk, defaults={'TENKHOA': tk, 'NGTLAP': ng})

    #Bảng GIAOVIEN (15 dòng)
    gv_data = [
        ('GV01', 'Hồ Thanh Sơn', 'PTS', 'GS', 'Nam', '1950-05-02', '2004-01-11', 5.00, 2250000, 'KHMT'),
        ('GV02', 'Trần Tâm Thanh', 'TS', 'PGS', 'Nam', '1965-12-17', '2004-04-20', 4.50, 2025000, 'HTTT'),
        ('GV03', 'Đỗ Nghiêm Phùng', 'TS', 'GS', 'Nữ', '1950-08-01', '2004-09-23', 4.00, 1800000, 'CNPM'),
        ('GV04', 'Trần Nam Sơn', 'TS', 'PGS', 'Nam', '1961-02-22', '2005-01-12', 4.50, 2025000, 'KTMT'),
        ('GV05', 'Mai Thanh Danh', 'ThS', 'GV', 'Nam', '1958-03-12', '2005-01-12', 3.00, 1350000, 'HTTT'),
        ('GV06', 'Trần Đoàn Hùng', 'TS', 'GV', 'Nam', '1953-03-11', '2005-01-12', 4.50, 2025000, 'KHMT'),
        ('GV07', 'Nguyễn Minh Tiến', 'ThS', 'GV', 'Nam', '1971-11-23', '2005-03-01', 4.00, 1800000, 'KHMT'),
        ('GV08', 'Lê Thị Trân', 'KS', None, 'Nữ', '1974-03-26', '2005-03-01', 1.69, 760500, 'KHMT'),
        ('GV09', 'Nguyễn Tố Lan', 'ThS', 'GV', 'Nữ', '1966-12-31', '2005-03-01', 4.00, 1800000, 'HTTT'),
        ('GV10', 'Lê Trần Anh Loan', 'KS', None, 'Nữ', '1972-07-17', '2005-03-01', 1.86, 837000, 'CNPM'),
        ('GV11', 'Hồ Thanh Tùng', 'CN', 'GV', 'Nam', '1980-01-12', '2005-05-15', 2.67, 1201500, 'MTT'),
        ('GV12', 'Trần Vân Anh', 'CN', None, 'Nữ', '1981-03-29', '2005-05-15', 1.69, 760500, 'CNPM'),
        ('GV13', 'Nguyễn Linh Đan', 'CN', None, 'Nữ', '1980-05-23', '2005-05-15', 1.69, 760500, 'KTMT'),
        ('GV14', 'Trương Minh Châu', 'ThS', 'GV', 'Nữ', '1976-11-30', '2005-05-15', 3.00, 1350000, 'MTT'),
        ('GV15', 'Lê Hà Thanh', 'ThS', 'GV', 'Nam', '1978-05-04', '2005-05-15', 3.00, 1350000, 'KHMT'),
    ]
    for mgv, ht, hv, hh, gt, ns, nvl, hs, ml, mk in gv_data:
        GiaoVien.objects.update_or_create(
            MAGV=mgv,
            defaults={'HOTEN': ht, 'HOCVI': hv, 'HOCHAM': hh, 'GIOITINH': gt, 'NGSINH': ns,
                      'NGVL': nvl, 'HESO': hs, 'MUCLUONG': ml, 'MAKHOA_id': mk}
        )

    # Cập nhật Trưởng khoa
    Khoa.objects.filter(MAKHOA='KHMT').update(TRGKHOA_id='GV01')
    Khoa.objects.filter(MAKHOA='HTTT').update(TRGKHOA_id='GV02')
    Khoa.objects.filter(MAKHOA='CNPM').update(TRGKHOA_id='GV04')
    Khoa.objects.filter(MAKHOA='MTT').update(TRGKHOA_id='GV03')

    #Bảng MONHOC (13 dòng)
    monhoc_data = [
        ('THDC', 'Tin học đại cương', 4, 1, 'KHMT'),
        ('CTRR', 'Cấu trúc rời rạc', 5, 0, 'KHMT'),
        ('CSDL', 'Cơ sở dữ liệu', 3, 1, 'HTTT'),
        ('CTDLGT', 'Cấu trúc dữ liệu và giải thuật', 3, 1, 'KHMT'),
        ('PTTKTT', 'Phân tích thiết kế thuật toán', 3, 0, 'KHMT'),
        ('DHMT', 'Đồ họa máy tính', 3, 1, 'KHMT'),
        ('KTMT', 'Kiến trúc máy tính', 3, 0, 'KTMT'),
        ('TKCSDL', 'Thiết kế cơ sở dữ liệu', 3, 1, 'HTTT'),
        ('PTTKHTTT', 'Phân tích thiết kế hệ thống thông tin', 4, 1, 'HTTT'),
        ('HDH', 'Hệ điều hành', 4, 0, 'KTMT'),
        ('NMCNPM', 'Nhập môn công nghệ phần mềm', 3, 0, 'CNPM'),
        ('LTCFW', 'Lập trình C for Windows', 3, 1, 'CNPM'),
        ('LTHDT', 'Lập trình hướng đối tượng', 3, 1, 'CNPM'),
    ]
    for mmh, tmh, tclt, tcth, mk in monhoc_data:
        MonHoc.objects.update_or_create(
            MAMH=mmh, defaults={'TENMH': tmh, 'TCLT': tclt, 'TCTH': tcth, 'MAKHOA_id': mk}
        )

    #Bảng DIEUKIEN (8 dòng)
    dieukien_data = [
        ('CSDL', 'CTRR'), ('CSDL', 'CTDLGT'), ('CTDLGT', 'THDC'), ('PTTKTT', 'THDC'),
        ('PTTKTT', 'CTDLGT'), ('DHMT', 'THDC'), ('LTHDT', 'THDC'), ('PTTKHTTT', 'CSDL'),
    ]
    for mmh, mmh_t in dieukien_data:
        DieuKien.objects.get_or_create(MAMH_id=mmh, MAMH_TRUOC_id=mmh_t)

    #Bảng LOP (3 dòng)
    lop_data = [
        ('K11', 'Lớp 1 khóa 1', 11, 'GV07'),
        ('K12', 'Lớp 2 khóa 1', 12, 'GV09'),
        ('K13', 'Lớp 3 khóa 1', 12, 'GV14'),
    ]
    for ml, tl, ss, gvcn in lop_data:
        Lop.objects.update_or_create(MALOP=ml, defaults={'TENLOP': tl, 'SISO': ss, 'MAGVCN_id': gvcn})

    #Bảng HOCVIEN (35 dòng)
    hocvien_data = [
        ('K1101', 'Nguyễn Văn', 'A', '1986-01-27', 'Nam', 'TP. Hồ Chí Minh', 'K11'),
        ('K1102', 'Trần Ngọc', 'Hân', '1986-03-14', 'Nữ', 'Kiên Giang', 'K11'),
        ('K1103', 'Hà Duy', 'Lập', '1986-04-18', 'Nam', 'Nghệ An', 'K11'),
        ('K1104', 'Trần Ngọc', 'Linh', '1986-03-30', 'Nữ', 'Tây Ninh', 'K11'),
        ('K1105', 'Trần Minh', 'Long', '1986-02-27', 'Nam', 'TP. Hồ Chí Minh', 'K11'),
        ('K1106', 'Lê Nhật', 'Minh', '1986-01-24', 'Nam', 'TP. Hồ Chí Minh', 'K11'),
        ('K1107', 'Nguyễn Như', 'Nhựt', '1986-01-27', 'Nam', 'Hà Nội', 'K11'),
        ('K1108', 'Nguyễn Mạnh', 'Tâm', '1986-02-27', 'Nam', 'Kiên Giang', 'K11'),
        ('K1109', 'Phan Thị Thanh', 'Tâm', '1986-01-27', 'Nữ', 'Vĩnh Long', 'K11'),
        ('K1110', 'Lê Hoài', 'Thương', '1986-02-05', 'Nữ', 'Cần Thơ', 'K11'),
        ('K1111', 'Lê Hà', 'Vinh', '1986-12-25', 'Nam', 'Vĩnh Long', 'K11'),
        ('K1201', 'Nguyễn Văn', 'B', '1986-02-11', 'Nam', 'TP. Hồ Chí Minh', 'K12'),
        ('K1202', 'Nguyễn Thị Kim', 'Duyên', '1986-01-18', 'Nữ', 'TP. Hồ Chí Minh', 'K12'),
        ('K1203', 'Trần Thị Kim', 'Duyên', '1986-09-17', 'Nữ', 'TP. Hồ Chí Minh', 'K12'),
        ('K1204', 'Trương Mỹ', 'Hạnh', '1986-05-19', 'Nữ', 'Đồng Nai', 'K12'),
        ('K1205', 'Nguyễn Thanh', 'Nam', '1986-04-17', 'Nam', 'TP. Hồ Chí Minh', 'K12'),
        ('K1206', 'Nguyễn Thị Trúc', 'Thanh', '1986-03-04', 'Nữ', 'Kiên Giang', 'K12'),
        ('K1207', 'Trần Thị Bích', 'Thủy', '1986-02-08', 'Nữ', 'Nghệ An', 'K12'),
        ('K1208', 'Huỳnh Thị Kim', 'Triều', '1986-04-08', 'Nữ', 'Tây Ninh', 'K12'),
        ('K1209', 'Phạm Thanh', 'Triều', '1986-02-23', 'Nam', 'TP. Hồ Chí Minh', 'K12'),
        ('K1210', 'Ngô Thanh', 'Tuấn', '1986-02-14', 'Nam', 'TP. Hồ Chí Minh', 'K12'),
        ('K1211', 'Đỗ Thị', 'Xuân', '1986-03-09', 'Nữ', 'Hà Nội', 'K12'),
        ('K1212', 'Lê Thị Phi', 'Yến', '1986-03-12', 'Nữ', 'TP. Hồ Chí Minh', 'K12'),
        ('K1301', 'Nguyễn Thị Kim', 'Cúc', '1986-06-09', 'Nữ', 'Kiên Giang', 'K13'),
        ('K1302', 'Trương Thị Mỹ', 'Hiền', '1986-03-18', 'Nữ', 'Nghệ An', 'K13'),
        ('K1303', 'Lê Đức', 'Hiền', '1986-03-21', 'Nam', 'Tây Ninh', 'K13'),
        ('K1304', 'Lê Quang', 'Hiền', '1986-04-18', 'Nam', 'TP. Hồ Chí Minh', 'K13'),
        ('K1305', 'Lê Thị', 'Hương', '1986-03-27', 'Nữ', 'TP. Hồ Chí Minh', 'K13'),
        ('K1306', 'Nguyễn Thái', 'Hữu', '1986-03-30', 'Nam', 'Hà Nội', 'K13'),
        ('K1307', 'Trần Minh', 'Mẫn', '1986-05-28', 'Nam', 'TP. Hồ Chí Minh', 'K13'),
        ('K1308', 'Nguyễn Hiếu', 'Nghĩa', '1986-04-08', 'Nam', 'Kiên Giang', 'K13'),
        ('K1309', 'Nguyễn Trung', 'Nghĩa', '1987-01-18', 'Nam', 'Nghệ An', 'K13'),
        ('K1310', 'Trần Thị Hồng', 'Thắm', '1986-04-22', 'Nữ', 'Tây Ninh', 'K13'),
        ('K1311', 'Trần Minh', 'Thức', '1986-04-04', 'Nam', 'TP. Hồ Chí Minh', 'K13'),
        ('K1312', 'Nguyễn Thị Kim', 'Yến', '1986-09-07', 'Nữ', 'TP. Hồ Chí Minh', 'K13'),
    ]
    for mhv, HO, TEN, ns, gt, nois, ml in hocvien_data:
        HocVien.objects.update_or_create(
            MAHV=mhv, defaults={'HO': HO, 'TEN': TEN, 'NGSINH': ns, 'GIOITINH': gt, 'NOISINH': nois, 'MALOP_id': ml}
        )

    # Cập nhật Lớp trưởng
    Lop.objects.filter(MALOP='K11').update(TRGLOP_id='K1108')
    Lop.objects.filter(MALOP='K12').update(TRGLOP_id='K1205')
    Lop.objects.filter(MALOP='K13').update(TRGLOP_id='K1305')

    #Bảng GIANGDAY (16 dòng)
    giangday_data = [
        ('K11', 'THDC', 'GV07', 1, 2006, '2006-01-02', '2006-05-12'),
        ('K12', 'THDC', 'GV06', 1, 2006, '2006-01-02', '2006-05-12'),
        ('K13', 'THDC', 'GV15', 1, 2006, '2006-01-02', '2006-05-12'),
        ('K11', 'CTRR', 'GV02', 1, 2006, '2006-01-09', '2006-05-17'),
        ('K12', 'CTRR', 'GV02', 1, 2006, '2006-01-09', '2006-05-17'),
        ('K13', 'CTRR', 'GV08', 1, 2006, '2006-01-09', '2006-05-17'),
        ('K11', 'CSDL', 'GV05', 2, 2006, '2006-06-01', '2006-07-15'),
        ('K12', 'CSDL', 'GV09', 2, 2006, '2006-06-01', '2006-07-15'),
        ('K13', 'CTDLGT', 'GV15', 2, 2006, '2006-06-01', '2006-07-15'),
        ('K13', 'CSDL', 'GV05', 3, 2006, '2006-08-01', '2006-12-15'),
        ('K13', 'DHMT', 'GV07', 3, 2006, '2006-08-01', '2006-12-15'),
        ('K11', 'CTDLGT', 'GV15', 3, 2006, '2006-08-01', '2006-12-15'),
        ('K12', 'CTDLGT', 'GV15', 3, 2006, '2006-08-01', '2006-12-15'),
        ('K11', 'HDH', 'GV04', 1, 2007, '2007-01-02', '2007-02-18'),
        ('K12', 'HDH', 'GV04', 1, 2007, '2007-01-02', '2007-03-20'),
        ('K11', 'DHMT', 'GV07', 1, 2007, '2007-02-18', '2007-03-20'),
    ]
    for ml, mmh, mgv, hk, NAM, tn, dn in giangday_data:
        GiangDay.objects.update_or_create(
            MALOP_id=ml, MAMH_id=mmh,
            defaults={'MAGV_id': mgv, 'HOCKY': hk, 'NAM': NAM, 'TUNGAY': tn, 'DENNGAY': dn}
        )

    # Bảng KETQUATHI (66 dòng)
    ketquathi_data = [
        ('K1101', 'CSDL', 1, '2006-07-20', 10.00, 'Đạt'),
        ('K1101', 'CTDLGT', 1, '2006-12-28', 9.00, 'Đạt'),
        ('K1101', 'THDC', 1, '2006-05-20', 9.00, 'Đạt'),
        ('K1101', 'CTRR', 1, '2006-05-13', 9.50, 'Đạt'),
        ('K1102', 'CSDL', 1, '2006-07-20', 4.00, 'Không đạt'),
        ('K1102', 'CSDL', 2, '2006-07-27', 4.25, 'Không đạt'),
        ('K1102', 'CSDL', 3, '2006-08-10', 4.50, 'Không đạt'),
        ('K1102', 'CTDLGT', 1, '2006-12-28', 4.50, 'Không đạt'),
        ('K1102', 'CTDLGT', 2, '2007-01-05', 4.00, 'Không đạt'),
        ('K1102', 'CTDLGT', 3, '2007-01-15', 6.00, 'Đạt'),
        ('K1102', 'THDC', 1, '2006-05-20', 5.00, 'Đạt'),
        ('K1102', 'CTRR', 1, '2006-05-13', 7.00, 'Đạt'),
        ('K1103', 'CSDL', 1, '2006-07-20', 3.50, 'Không đạt'),
        ('K1103', 'CSDL', 2, '2006-07-27', 8.25, 'Đạt'),
        ('K1103', 'CTDLGT', 1, '2006-12-28', 7.00, 'Đạt'),
        ('K1103', 'THDC', 1, '2006-05-20', 8.00, 'Đạt'),
        ('K1103', 'CTRR', 1, '2006-05-13', 6.50, 'Đạt'),
        ('K1104', 'CSDL', 1, '2006-07-20', 3.75, 'Không đạt'),
        ('K1104', 'CTDLGT', 1, '2006-12-28', 4.00, 'Không đạt'),
        ('K1104', 'THDC', 1, '2006-05-20', 4.00, 'Không đạt'),
        ('K1104', 'CTRR', 1, '2006-05-13', 4.00, 'Không đạt'),
        ('K1104', 'CTRR', 2, '2006-05-20', 3.50, 'Không đạt'),
        ('K1104', 'CTRR', 3, '2006-06-30', 4.00, 'Không đạt'),
        ('K1201', 'CSDL', 1, '2006-07-20', 6.00, 'Đạt'),
        ('K1201', 'CTDLGT', 1, '2006-12-28', 5.00, 'Đạt'),
        ('K1201', 'THDC', 1, '2006-05-20', 8.50, 'Đạt'),
        ('K1201', 'CTRR', 1, '2006-05-13', 9.00, 'Đạt'),
        ('K1202', 'CSDL', 1, '2006-07-20', 8.00, 'Đạt'),
        ('K1202', 'CTDLGT', 1, '2006-12-28', 4.00, 'Không đạt'),
        ('K1202', 'CTDLGT', 2, '2007-01-05', 5.00, 'Đạt'),
        ('K1202', 'THDC', 1, '2006-05-20', 4.00, 'Không đạt'),
        ('K1202', 'THDC', 2, '2006-05-27', 4.00, 'Không đạt'),
        ('K1202', 'CTRR', 1, '2006-05-13', 3.00, 'Không đạt'),
        ('K1202', 'CTRR', 2, '2006-05-20', 4.00, 'Không đạt'),
        ('K1202', 'CTRR', 3, '2006-06-30', 6.25, 'Đạt'),
        ('K1203', 'CSDL', 1, '2006-07-20', 9.25, 'Đạt'),
        ('K1203', 'CTDLGT', 1, '2006-12-28', 9.50, 'Đạt'),
        ('K1203', 'THDC', 1, '2006-05-20', 10.00, 'Đạt'),
        ('K1203', 'CTRR', 1, '2006-05-13', 10.00, 'Đạt'),
        ('K1204', 'CSDL', 1, '2006-07-20', 8.50, 'Đạt'),
        ('K1204', 'CTDLGT', 1, '2006-12-28', 6.75, 'Đạt'),
        ('K1204', 'THDC', 1, '2006-05-20', 4.00, 'Không đạt'),
        ('K1204', 'CTRR', 1, '2006-05-13', 6.00, 'Đạt'),
        ('K1301', 'CSDL', 1, '2006-12-20', 4.25, 'Không đạt'),
        ('K1301', 'CTDLGT', 1, '2006-07-25', 8.00, 'Đạt'),
        ('K1301', 'THDC', 1, '2006-05-20', 7.75, 'Đạt'),
        ('K1301', 'CTRR', 1, '2006-05-13', 8.00, 'Đạt'),
        ('K1302', 'CSDL', 1, '2006-12-20', 6.75, 'Đạt'),
        ('K1302', 'CTDLGT', 1, '2006-07-25', 5.00, 'Đạt'),
        ('K1302', 'THDC', 1, '2006-05-20', 8.00, 'Đạt'),
        ('K1302', 'CTRR', 1, '2006-05-13', 8.50, 'Đạt'),
        ('K1303', 'CSDL', 1, '2006-12-20', 4.00, 'Không đạt'),
        ('K1303', 'CTDLGT', 1, '2006-07-25', 4.50, 'Không đạt'),
        ('K1303', 'CTDLGT', 2, '2006-08-07', 4.00, 'Không đạt'),
        ('K1303', 'CTDLGT', 3, '2006-08-15', 4.25, 'Không đạt'),
        ('K1303', 'THDC', 1, '2006-05-20', 4.50, 'Không đạt'),
        ('K1303', 'CTRR', 1, '2006-05-13', 3.25, 'Không đạt'),
        ('K1303', 'CTRR', 2, '2006-05-20', 5.00, 'Đạt'),
        ('K1304', 'CSDL', 1, '2006-12-20', 7.75, 'Đạt'),
        ('K1304', 'CTDLGT', 1, '2006-07-25', 9.75, 'Đạt'),
        ('K1304', 'THDC', 1, '2006-05-20', 5.50, 'Đạt'),
        ('K1304', 'CTRR', 1, '2006-05-13', 5.00, 'Đạt'),
        ('K1305', 'CSDL', 1, '2006-12-20', 9.25, 'Đạt'),
        ('K1305', 'CTDLGT', 1, '2006-07-25', 10.00, 'Đạt'),
        ('K1305', 'THDC', 1, '2006-05-20', 8.00, 'Đạt'),
        ('K1305', 'CTRR', 1, '2006-05-13', 10.00, 'Đạt'),
    ]
    for mhv, mmh, lt, nt, d, kq in ketquathi_data:
        KetQuaThi.objects.update_or_create(
            MAHV_id=mhv, MAMH_id=mmh, LANTHI=lt,
            defaults={'NGTHI': nt, 'DIEM': d, 'KQUA': kq}
        )

    for ml, hv in [('K11', 'K1108'), ('K12', 'K1205'), ('K13', 'K1305')]:
        Lop.objects.filter(MALOP=ml).update(TRGLOP_id=hv)

    # kiểm tra tổng số dòng
    counts = [
        Khoa.objects.count(), GiaoVien.objects.count(), MonHoc.objects.count(),
        DieuKien.objects.count(), Lop.objects.count(), HocVien.objects.count(),
        GiangDay.objects.count(), KetQuaThi.objects.count()
    ]
    print(f"📊 KIỂM TRA SỐ DÒNG: {counts} (Tổng cộng: {sum(counts)}/161 dòng)")
    print("🎉 HOÀN THÀNH 100% NẠP DỮ LIỆU!")
