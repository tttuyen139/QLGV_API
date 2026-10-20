"""Đề xuất có chữ ký; lưu đúng lịch admin đã xem trước."""
import hashlib
import json

from django.apps import apps
from django.core import signing
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from rest_framework.exceptions import ValidationError

from . import services
from .models import Phong, LichHoc

SALT = 'qlgv.ai.admin.preview.v1'


def fingerprint():
    data = {}
    for label in ['KHOA.Khoa', 'GIAOVIEN.GiaoVien', 'MONHOC.MonHoc', 'DIEUKIEN.DieuKien',
                  'LOP.Lop', 'HOCVIEN.HocVien', 'GIANGDAY.GiangDay', 'KETQUATHI.KetQuaThi',
                  'AI.Phong', 'AI.LichHoc']:
        model = apps.get_model(label)
        fields = [f.attname for f in model._meta.fields if not f.name == 'pk']
        rows = list(model.objects.values(*fields))
        data[label] = sorted(rows, key=lambda r: json.dumps(r, cls=DjangoJSONEncoder, sort_keys=True))
    raw = json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def preview(HOCKY, NAM, user_id):
    before = fingerprint()
    result = services.xep_lich(HOCKY, NAM, luu=False)
    after = fingerprint()
    if before != after:
        raise ValidationError('Dữ liệu vừa thay đổi. Vui lòng tạo lại lịch đề xuất.')
    if not result['thanh_cong']:
        return result, None
    payload = {'HOCKY': HOCKY, 'NAM': NAM, 'user_id': user_id, 'fingerprint': after, 'lich': result['lich']}
    return result, signing.dumps(payload, salt=SALT, compress=True)


def confirm(token, user_id):
    try:
        payload = signing.loads(token, salt=SALT, max_age=600)
    except signing.BadSignature:
        raise ValidationError('Đề xuất không hợp lệ hoặc đã quá 10 phút. Vui lòng tạo lại.')
    if payload.get('user_id') != user_id:
        raise ValidationError('Đề xuất không thuộc tài khoản đang đăng nhập.')
    with transaction.atomic():
        services._lock()
        if fingerprint() != payload['fingerprint']:
            raise ValidationError('Dữ liệu đã thay đổi kể từ lúc xem trước. Vui lòng tạo lại đề xuất.')
        gd = services._ds_gd()
        expected = {k for k, g in gd.items() if (g.HOCKY, g.NAM) == (payload['HOCKY'], payload['NAM'])}
        proposed = payload['lich']
        keys = [(r['MALOP'], r['MAMH']) for r in proposed]
        if set(keys) != expected or len(keys) != len(expected):
            raise ValidationError('Đề xuất thiếu hoặc lặp phân công giảng dạy.')
        rooms = {p.pk: p for p in Phong.objects.all()}
        existing = {(l.MALOP_id, l.MAMH_id): l for l in LichHoc.objects.all()}
        merged = {k: l for k, l in existing.items() if k not in expected}
        for r in proposed:
            k = r['MALOP'], r['MAMH']
            if r['MAPHONG'] not in rooms or r['THU'] not in range(2, 8) or r['CA'] not in range(1, 5):
                raise ValidationError('Phòng hoặc khung giờ không hợp lệ.')
            old = existing.get(k)
            l = LichHoc(MALOP_id=k[0], MAMH_id=k[1], MAPHONG_id=r['MAPHONG'],
                        THU=r['THU'], CA=r['CA'], SISO_TOIDA=rooms[r['MAPHONG']].SUCCHUA,
                        DANGKY=list(old.DANGKY) if old else [])
            if services._si_so(l, gd[k]) > l.SISO_TOIDA:
                raise ValidationError('Sức chứa không đủ cho học viên hiện có.')
            merged[k] = l
        keys = list(merged)
        students = {k: services._hoc_vien(l, gd[k]) for k, l in merged.items() if k in gd}
        for i, a in enumerate(keys):
            if a not in gd:
                raise ValidationError('Có lịch lưu không còn phân công GIANGDAY tương ứng.')
            for b in keys[i+1:]:
                if b not in gd:
                    raise ValidationError('Có lịch lưu không còn phân công GIANGDAY tương ứng.')
                l, m = merged[a], merged[b]
                if not services._trung_ngay(gd[a], gd[b]) or (l.THU, l.CA) != (m.THU, m.CA):
                    continue
                if l.MAPHONG_id == m.MAPHONG_id or gd[a].MAGV_id == gd[b].MAGV_id or a[0] == b[0] or students[a] & students[b]:
                    raise ValidationError('Lịch có xung đột phòng, giáo viên hoặc học viên.')
        for r in proposed:
            LichHoc.objects.update_or_create(MALOP_id=r['MALOP'], MAMH_id=r['MAMH'], defaults={
                'MAPHONG_id': r['MAPHONG'], 'THU': r['THU'], 'CA': r['CA'],
                'SISO_TOIDA': rooms[r['MAPHONG']].SUCCHUA})
        return len(proposed)
