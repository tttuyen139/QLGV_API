from django.urls import path

from .views import GiaoVienListAPI

urlpatterns = [
    path('api/giaovien/', GiaoVienListAPI.as_view(), name='gv_list'),
]
