from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db import transaction, OperationalError
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from rest_framework.exceptions import ValidationError

from . import services, admin_services
from .admin_forms import XepLichForm, PhongAdminForm
from .models import Phong, LichHoc


@admin.register(Phong)
class PhongAdmin(admin.ModelAdmin):
    form = PhongAdminForm
    list_display = ('MAPHONG', 'SUCCHUA', 'LOAI')
    search_fields = ('MAPHONG',)
    actions = None

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST':
            with transaction.atomic():
                services._lock()
                return super().changeform_view(request, object_id, form_url, extra_context)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_readonly_fields(self, request, obj=None):
        return ('MAPHONG',) if obj else ()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LichHoc)
class LichHocAdmin(admin.ModelAdmin):
    list_display = ('MALOP', 'MAMH', 'MAPHONG', 'THU', 'CA', 'SISO_TOIDA', 'so_dang_ky_them')
    list_filter = ('MALOP', 'MAPHONG', 'THU', 'CA')
    search_fields = ('MALOP__MALOP', 'MAMH__MAMH', 'MAMH__TENMH')
    list_select_related = ('MALOP', 'MAMH', 'MAPHONG')
    change_list_template = 'admin/AI/lichhoc/change_list.html'
    actions = None

    @admin.display(description='Đăng ký thêm')
    def so_dang_ky_them(self, obj):
        return len(obj.DANGKY)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        return [path('xep-lich/', self.admin_site.admin_view(self.xep_lich_view),
                     name='AI_lichhoc_xep_lich')] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context={
            **(extra_context or {}), 'can_schedule': request.user.has_perm('AI.change_lichhoc')})

    def xep_lich_view(self, request):
        if not request.user.has_perm('AI.change_lichhoc'):
            raise PermissionDenied
        form = XepLichForm(request.POST or None)
        result, token, rows = None, None, []
        if request.method == 'POST':
            action = request.POST.get('action')
            try:
                if action == 'confirm':
                    count = admin_services.confirm(request.POST.get('preview_token', ''), request.user.pk)
                    self.message_user(request, f'Đã lưu đúng {count} lịch đã xem trước.', messages.SUCCESS)
                    return HttpResponseRedirect(reverse('admin:AI_lichhoc_changelist'))
                if action == 'preview' and form.is_valid():
                    result, token = admin_services.preview(**form.cleaned_data, user_id=request.user.pk)
                    if not result['thanh_cong']:
                        form.add_error(None, result.get('thong_bao', 'Không tìm được lịch phù hợp.'))
                    else:
                        gd = services._ds_gd()
                        for row in result['lich']:
                            g = gd[(row['MALOP'], row['MAMH'])]
                            rows.append({**row, 'TENMH': g.MAMH.TENMH, 'GIAOVIEN': g.MAGV.HOTEN,
                                         'TUNGAY': g.TUNGAY, 'DENNGAY': g.DENNGAY})
                elif action not in ('preview', 'confirm'):
                    form.add_error(None, 'Thao tác không hợp lệ.')
            except ValidationError as exc:
                form.add_error(None, ' '.join(map(str, exc.detail)) if isinstance(exc.detail, list) else str(exc.detail))
            except OperationalError:
                form.add_error(None, 'Dữ liệu đang được cập nhật. Vui lòng thử lại.')
        context = {
            **self.admin_site.each_context(request), 'title': 'AI xếp lịch học',
            'opts': self.model._meta, 'form': form, 'result': result, 'rows': rows,
            'preview_token': token, 'phong_url': reverse('admin:AI_phong_changelist'),
            'list_url': reverse('admin:AI_lichhoc_changelist'),
        }
        return TemplateResponse(request, 'admin/AI/lichhoc/xep_lich.html', context)
