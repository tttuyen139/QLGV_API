from django.urls import path

from .views import HocVienListAPI

urlpatterns = [
    path('api/hocvien/', HocVienListAPI.as_view(), name='hv_list'),
]
