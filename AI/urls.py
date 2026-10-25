from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('phong', views.PhongViewSet)
router.register('lich-hoc', views.LichHocViewSet, basename='lich-hoc')

urlpatterns = [

    path('api/ai/de-xuat-hoc-phan/', views.AIGoiYDangKyView.as_view(), name='de_xuat_hoc_phan_chuan'),
    path('api/ai/xac-nhan-hoc-phan/', views.AIXacNhanDangKyView.as_view(), name='xac_nhan_hoc_phan_chuan'),
    path('api/ai/xep-thoi-khoa-bieu/', views.AIXepLichView.as_view(), name='xep_tkb_chuan'),


    path('api/ai/goi-y-dang-ky/', views.AIGoiYDangKyView.as_view()),
    path('api/ai/xac-nhan-dang-ky/', views.AIXacNhanDangKyView.as_view()),
    path('api/ai/xep-lich/', views.AIXepLichView.as_view()),
    path('api/', include(router.urls)),
]