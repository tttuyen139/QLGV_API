from django.urls import path
from . import student_portal as views

urlpatterns = [
    path('hoc-vien/lop/', views.MyClass.as_view(), name='student-class'),
    path('hoc-vien/ket-qua-thi/', views.MyResults.as_view(), name='student-results'),
    path('hoc-vien/hoc-phan/', views.CourseCatalog.as_view(), name='student-catalog'),
    path('hoc-vien/', views.StudentHome.as_view(), name='student-home'),
    path('hoc-vien/lich-hoc/', views.MySchedule.as_view(), name='student-schedule'),
    path('hoc-vien/diem-trung-binh/', views.MyAverage.as_view(), name='student-average'),
    path('hoc-vien/mon-tien-quyet/', views.MyPrerequisites.as_view(), name='student-prerequisites'),
    path('hoc-vien/goi-y-hoc-phan/', views.StudentSuggest.as_view(), name='student-suggest'),
    path('hoc-vien/xac-nhan-dang-ky/', views.StudentConfirm.as_view(), name='student-confirm'),
    path('hoc-vien/tro-ly/', views.StudentChat.as_view(), name='student-chat'),
]
