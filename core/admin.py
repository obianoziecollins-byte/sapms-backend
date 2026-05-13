from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, Course, Prerequisite, Enrollment


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    readonly_fields = ('is_on_probation',)


class UserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline,)
    list_display = ('username', 'get_student_id', 'email', 'is_staff')

    def get_student_id(self, obj):
        return obj.profile.student_id if hasattr(obj, 'profile') else 'No Profile'
    get_student_id.short_description = 'Student ID'


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display  = ('course', 'required_course', 'min_grade')
    list_filter   = ('min_grade',)
    search_fields = ('course__course_code', 'required_course__course_code')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(Enrollment)