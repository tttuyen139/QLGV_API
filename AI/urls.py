from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('phong', views.PhongViewSet)
router.register('lich-hoc', views.LichHocViewSet, basename='lich-hoc')
urlpatterns = [
    path('api/ai/xep-lich/', views.AIXepLichView.as_view()),
    path('api/ai/goi-y-dang-ky/', views.AIGoiYDangKyView.as_view()),
    path('api/ai/xac-nhan-dang-ky/', views.AIXacNhanDangKyView.as_view()),
    path('api/', include(router.urls)),
]
