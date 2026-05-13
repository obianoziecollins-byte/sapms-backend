from django.contrib import admin
from django.urls import path
from core.views import (
    login_student, register_student,
    get_profile, update_profile,
    list_courses, list_prerequisites,
    enroll_course, drop_course,
)

urlpatterns = [
    path('admin/',                          admin.site.urls),
    path('api/login/',                      login_student,       name='login'),
    path('api/register/',                   register_student,    name='register'),
    path('api/profile/',                    get_profile,         name='get-profile'),
    path('api/profile/update/',             update_profile,      name='update-profile'),
    path('api/courses/',                    list_courses,        name='list-courses'),
    path('api/prerequisites/',              list_prerequisites,  name='list-prerequisites'),
    path('api/enroll/',                     enroll_course,       name='enroll-course'),
    path('api/enroll/<int:enrollment_id>/', drop_course,         name='drop-course'),
]