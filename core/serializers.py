from rest_framework import serializers
from .models import StudentProfile, Course, Enrollment, Prerequisite
from django.contrib.auth.models import User


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Course
        fields = ['course_code', 'title', 'credit_units', 'is_mandatory']


class EnrollmentSerializer(serializers.ModelSerializer):
    course        = CourseSerializer(read_only=True)
    display_name  = serializers.SerializerMethodField()
    grade_display = serializers.SerializerMethodField()

    class Meta:
        model  = Enrollment
        fields = ['id', 'grade', 'grade_display', 'semester', 'display_name', 'course']

    def get_display_name(self, obj):
        return str(obj)

    def get_grade_display(self, obj):
        return dict(Enrollment.GRADE_CHOICES).get(obj.grade, obj.grade)


class PrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Prerequisite
        fields = ['id', 'course_code', 'required_course_code', 'min_grade']


class StudentProfileSerializer(serializers.ModelSerializer):
    specialization_display = serializers.CharField(
        source='get_specialization_display', read_only=True)
    first_name  = serializers.CharField(source='user.first_name', read_only=True)
    last_name   = serializers.CharField(source='user.last_name',  read_only=True)
    username    = serializers.CharField(source='user.username',   read_only=True)
    email       = serializers.CharField(source='user.email',      read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta:
        model  = StudentProfile
        fields = [
            'id','username','first_name','last_name','email',
            'student_id','level','department',
            'specialization','specialization_display',
            'cgpa','is_on_probation','enrollments',
        ]