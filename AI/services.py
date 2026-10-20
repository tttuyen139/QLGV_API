"""Tối ưu CP-SAT; mọi ghi lịch/đăng ký được kiểm tra trong transaction."""

from collections import defaultdict
from itertools import combinations

from django.db import transaction
from rest_framework.exceptions import ValidationError
from ortools.sat.python import cp_model

from GIANGDAY.models import GiangDay
from HOCVIEN.models import HocVien
from KETQUATHI.models import KetQuaThi
from DIEUKIEN.models import DieuKien
from .models import Phong, LichHoc


def _trung_ngay(a, b):
    return a.TUNGAY <= b.DENNGAY and b.TUNGAY <= a.DENNGAY


def _ds_gd():
    return {(g.MALOP_id, g.MAMH_id): g for g in GiangDay.objects.select_related('MALOP', 'MAMH', 'MAGV')}


def _lock():
    # Khóa toàn bộ phòng theo thứ tự thống nhất: mutex dùng chung cho xếp lịch và xác nhận.
    # SQLite dùng BEGIN/khóa ghi toàn DB; production SQL Server dùng khóa hàng.
    list(Phong.objects.select_for_update().order_by('MAPHONG'))
    list(LichHoc.objects.select_for_update().order_by('id'))


def _si_so(lich, gd):
    # Học viên lớp gốc đã có lịch; chỉ cộng người đăng ký ngoài lớp.
    goc = set(HocVien.objects.filter(MALOP_id=gd.MALOP_id).values_list('MAHV', flat=True))
    return max(gd.MALOP.SISO, len(goc)) + len(set(lich.DANGKY) - goc)


def _hoc_vien(lich, gd):
    return set(HocVien.objects.filter(MALOP_id=gd.MALOP_id).values_list('MAHV', flat=True)) | set(lich.DANGKY)


def xep_lich(HOCKY, NAM, luu=False):
    with transaction.atomic():
        _lock()
        gd = _ds_gd()
        ds = [g for g in gd.values() if (g.HOCKY, g.NAM) == (HOCKY, NAM)]
        if not ds:
            return {'thanh_cong': False, 'lich': [], 'thong_bao': 'Học kỳ chưa có phân công GIANGDAY.'}
        phong = list(Phong.objects.order_by('MAPHONG'))
        cu = {(l.MALOP_id, l.MAMH_id): l for l in LichHoc.objects.all()}
        ngoai = [l for k, l in cu.items() if k in gd and gd[k] not in ds]
        model = cp_model.CpModel()
        bien, theo_lop, chi_phi = {}, defaultdict(list), []
        sv = {}
        for i, g in enumerate(ds):
            k = (g.MALOP_id, g.MAMH_id)
            l = cu.get(k)
            sv[i] = (
                _hoc_vien(l, g)
                if l
                else set(HocVien.objects.filter(MALOP_id=g.MALOP_id).values_list('MAHV', flat=True))
            )
            siso = _si_so(l, g) if l else max(g.MALOP.SISO, len(sv[i]))
            for thu in range(2, 8):
                for ca in range(1, 5):
                    for p in phong:
                        if p.SUCCHUA < siso:
                            continue
                        if any(
                            _trung_ngay(g, gd[(o.MALOP_id, o.MAMH_id)])
                            and (thu, ca) == (o.THU, o.CA)
                            and (
                                o.MAPHONG_id == p.pk
                                or gd[(o.MALOP_id, o.MAMH_id)].MAGV_id == g.MAGV_id
                                or sv[i] & _hoc_vien(o, gd[(o.MALOP_id, o.MAMH_id)])
                            )
                            for o in ngoai
                        ):
                            continue
                        v = model.new_bool_var(f'x_{i}_{thu}_{ca}_{p.pk}')
                        bien[i, thu, ca, p.pk] = v
                        theo_lop[i].append(v)
                        chi_phi.append(
                            ((50 if thu == 7 else 0) + (30 if ca == 4 else 0) + (p.SUCCHUA - siso) // 10) * v
                        )
            if not theo_lop[i]:
                return {'thanh_cong': False, 'lich': [], 'thong_bao': f'Không có phòng/khung giờ cho {k}.'}
            model.add_exactly_one(theo_lop[i])
        for i, j in combinations(range(len(ds)), 2):
            if not _trung_ngay(ds[i], ds[j]):
                continue
            chung = ds[i].MAGV_id == ds[j].MAGV_id or ds[i].MALOP_id == ds[j].MALOP_id or bool(sv[i] & sv[j])
            for thu in range(2, 8):
                for ca in range(1, 5):
                    if chung:
                        model.add_at_most_one(
                            [v for (idx, t, c, p), v in bien.items() if idx in (i, j) and (t, c) == (thu, ca)]
                        )
                    else:
                        for p in phong:
                            vs = [bien[idx, thu, ca, p.pk] for idx in (i, j) if (idx, thu, ca, p.pk) in bien]
                            if vs:
                                model.add_at_most_one(vs)
        model.minimize(sum(chi_phi))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {
                'thanh_cong': False,
                'lich': [],
                'thong_bao': 'Không tìm được lịch trong giới hạn 15 giây.',
            }
        lich = []
        for (i, thu, ca, p), v in bien.items():
            if solver.value(v):
                g = ds[i]
                row = {'MALOP': g.MALOP_id, 'MAMH': g.MAMH_id, 'THU': thu, 'CA': ca, 'MAPHONG': p}
                lich.append(row)
                if luu:
                    old = cu.get((g.MALOP_id, g.MAMH_id))
                    siso = _si_so(old, g) if old else max(g.MALOP.SISO, len(sv[i]))
                    LichHoc.objects.update_or_create(
                        MALOP_id=g.MALOP_id,
                        MAMH_id=g.MAMH_id,
                        defaults={
                            'THU': thu,
                            'CA': ca,
                            'MAPHONG_id': p,
                            'SISO_TOIDA': next(room.SUCCHUA for room in phong if room.pk == p),
                        },
                    )
        return {'thanh_cong': True, 'toi_uu': status == cp_model.OPTIMAL, 'da_luu': luu, 'lich': lich}


def _da_dat(hv):
    return set(KetQuaThi.objects.filter(MAHV=hv, DIEM__gte=5).values_list('MAMH_id', flat=True))


def _lich_sv(hv, gd):
    return [
        l
        for l in LichHoc.objects.all()
        if (l.MALOP_id, l.MAMH_id) in gd and (l.MALOP_id == hv.MALOP_id or hv.pk in l.DANGKY)
    ]


def kiem_tra(hv, l, gd, da_dk):
    g = gd.get((l.MALOP_id, l.MAMH_id))
    if not g:
        raise ValidationError('Lịch không có phân công GIANGDAY.')
    dat = _da_dat(hv)
    if l.MAMH_id in dat:
        raise ValidationError(f'Đã đạt môn {l.MAMH_id}.')
    truoc = set(DieuKien.objects.filter(MAMH_id=l.MAMH_id).values_list('MAMH_TRUOC_id', flat=True))
    if not truoc <= dat:
        raise ValidationError(f'Chưa đạt đầy đủ môn tiên quyết: {sorted(truoc-dat)}.')
    if hv.pk in l.DANGKY or hv.MALOP_id == l.MALOP_id:
        raise ValidationError('Học viên đã có trong lịch lớp này.')
    if _si_so(l, g) >= min(l.SISO_TOIDA, l.MAPHONG.SUCCHUA):
        raise ValidationError('Lớp đã đủ sĩ số.')
    for o in da_dk:
        og = gd[(o.MALOP_id, o.MAMH_id)]
        if (og.HOCKY, og.NAM) == (g.HOCKY, g.NAM) and o.MAMH_id == l.MAMH_id:
            raise ValidationError('Đã có môn này trong học kỳ.')
        if _trung_ngay(g, og) and (o.THU, o.CA) == (l.THU, l.CA):
            raise ValidationError('Trùng lịch học.')


def goi_y(hv, HOCKY, NAM, so_thich):
    gd = _ds_gd()
    dang = _lich_sv(hv, gd)
    trong_ky = [
        l
        for l in dang
        if (gd[(l.MALOP_id, l.MAMH_id)].HOCKY, gd[(l.MALOP_id, l.MAMH_id)].NAM) == (HOCKY, NAM)
    ]
    tc = sum(gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCLT + gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCTH for l in trong_ky)
    uv = []
    for l in LichHoc.objects.select_related('MAPHONG'):
        g = gd.get((l.MALOP_id, l.MAMH_id))
        if not g or (g.HOCKY, g.NAM) != (HOCKY, NAM) or l.THU in so_thich['thu_tranh']:
            continue
        try:
            kiem_tra(hv, l, gd, dang)
        except ValidationError:
            continue
        uv.append(l)

    def solve(min_tc):
        model = cp_model.CpModel()
        y = {l.pk: model.new_bool_var(f'y_{l.pk}') for l in uv}
        tong = tc + sum(
            (gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCLT + gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCTH) * y[l.pk]
            for l in uv
        )
        model.add(tong >= min_tc)
        model.add(tong <= so_thich['tin_chi_max'])
        for a, b in combinations(uv, 2):
            if a.MAMH_id == b.MAMH_id or (
                _trung_ngay(gd[(a.MALOP_id, a.MAMH_id)], gd[(b.MALOP_id, b.MAMH_id)])
                and (a.THU, a.CA) == (b.THU, b.CA)
            ):
                model.add_at_most_one(y[a.pk], y[b.pk])
        failed = set(
            KetQuaThi.objects.filter(MAHV=hv, DIEM__lt=5).values_list('MAMH_id', flat=True)
        ) - _da_dat(hv)
        model.maximize(
            sum(
                (
                    10 * (gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCLT + gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCTH)
                    + 30 * (l.MAMH_id in failed)
                    + 20 * (l.MAMH_id in so_thich['ma_mon_uu_tien'])
                    + 5 * (l.CA in so_thich['ca_uu_tien'])
                )
                * y[l.pk]
                for l in uv
            )
        )
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        status = solver.solve(model)
        return (
            ([l for l in uv if solver.value(y[l.pk])], status == cp_model.OPTIMAL)
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
            else (None, False)
        )

    if tc >= so_thich['tin_chi_max']:
        return {'de_xuat': [], 'tong_tin_chi': tc, 'ghi_chu': 'Đã đủ số tín chỉ tối đa.', 'toi_uu': False}
    chon, opt = solve(so_thich['tin_chi_min'])
    note = ''
    if chon is None:
        chon, opt = solve(0)
        note = 'Chưa đạt số tín chỉ tối thiểu; trả phương án khả thi trong giới hạn thời gian.'
    chon = chon or []
    return {
        'de_xuat': [
            {
                'id': l.pk,
                'MALOP': l.MALOP_id,
                'MAMH': l.MAMH_id,
                'THU': l.THU,
                'CA': l.CA,
                'MAPHONG': l.MAPHONG_id,
            }
            for l in chon
        ],
        'tong_tin_chi': tc
        + sum(gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCLT + gd[(l.MALOP_id, l.MAMH_id)].MAMH.TCTH for l in chon),
        'ghi_chu': note,
        'toi_uu': opt,
    }


def xac_nhan(hv, ids):
    with transaction.atomic():
        _lock()
        hv = HocVien.objects.select_for_update().get(pk=hv.pk)
        gd = _ds_gd()
        dang = _lich_sv(hv, gd)
        ds = list(LichHoc.objects.select_related('MAPHONG').filter(id__in=ids).order_by('id'))
        if len(ds) != len(ids):
            raise ValidationError('Danh sách chứa lịch không tồn tại hoặc bị lặp.')
        for l in ds:
            kiem_tra(hv, l, gd, dang)
            l.DANGKY = [*l.DANGKY, hv.pk]
            l.save(update_fields=['DANGKY'])
            dang.append(l)
        return {'da_dang_ky': [l.pk for l in ds]}
