from django.urls import path

from .views import MonHocListAPI

urlpatterns = [
    path('api/monhoc/', MonHocListAPI.as_view(), name='mh_list'),
]
