from rest_framework import generics, permissions
from .models import StudentProfile, Course, Enrollment, Prerequisite
from .serializers import StudentProfileSerializer, CourseSerializer, EnrollmentSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class StudentProfileList(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
def register_student(request):
    data = request.data
    try:
        full_name = data.get('full_name', '').strip()
        parts     = full_name.split(' ', 1)
        user = User.objects.create_user(
            username=data['username'], password=data['password'],
            email=data.get('email', ''),
            first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
        )
        profile = user.profile
        profile.student_id     = data['student_id']
        profile.specialization = data['specialization']
        profile.save()
        return Response({"message": "Registration successful!"}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['POST'])
def login_student(request):
    user = authenticate(username=request.data.get('username'),
                        password=request.data.get('password'))
    if user:
        return Response({
            "message":    "Login successful",
            "username":   user.username,
            "student_id": user.profile.student_id if hasattr(user, 'profile') else None,
            "first_name": user.first_name,
        }, status=200)
    return Response({"error": "Invalid credentials"}, status=401)


@api_view(['GET'])
def get_profile(request):
    username = request.query_params.get('username')
    if not username:
        return Response({"error": "Username is required."}, status=400)
    try:
        profile = User.objects.get(username=username).profile
        return Response(StudentProfileSerializer(profile).data, status=200)
    except (User.DoesNotExist, StudentProfile.DoesNotExist) as e:
        return Response({"error": str(e)}, status=404)


@api_view(['PATCH'])
def update_profile(request):
    username = request.query_params.get('username')
    if not username:
        return Response({"error": "Username is required."}, status=400)
    try:
        user    = User.objects.get(username=username)
        profile = user.profile
        data    = request.data
        if 'first_name'    in data: user.first_name = data['first_name'].strip()
        if 'last_name'     in data: user.last_name  = data['last_name'].strip()
        if 'email'         in data: user.email      = data['email'].strip()
        user.save()
        if 'level'          in data: profile.level          = int(data['level'])
        if 'specialization' in data: profile.specialization = data['specialization']
        if 'cgpa'           in data: profile.cgpa           = data['cgpa']
        profile.save()
        return Response(StudentProfileSerializer(profile).data, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
def list_courses(request):
    courses = Course.objects.all().order_by('course_code')
    return Response(CourseSerializer(courses, many=True).data, status=200)


@api_view(['GET'])
def list_prerequisites(request):
    """
    GET /api/prerequisites/
    Returns all prerequisite rules so the frontend can validate
    whether a student has completed required courses before enrolling.
    """
    data = [
        {
            'course_code':          p.course.course_code,
            'required_course_code': p.required_course.course_code,
            'required_course_title':p.required_course.title,
            'min_grade':            p.min_grade,
        }
        for p in Prerequisite.objects.select_related('course', 'required_course').all()
    ]
    return Response(data, status=200)


@api_view(['POST'])
def enroll_course(request):
    username    = request.data.get('username')
    course_code = request.data.get('course_code')
    semester    = request.data.get('semester')
    grade       = request.data.get('grade', 'IP')
    if not all([username, course_code, semester]):
        return Response({"error": "username, course_code, and semester are required."}, status=400)
    try:
        user    = User.objects.get(username=username)
        profile = user.profile
        course  = Course.objects.get(course_code=course_code)
        if Enrollment.objects.filter(student=profile, course=course, semester=semester).exists():
            return Response(
                {"error": f"Already enrolled in {course_code} for {semester} semester."},
                status=400
            )
        enrollment = Enrollment.objects.create(
            student=profile, course=course, semester=semester, grade=grade
        )
        return Response(EnrollmentSerializer(enrollment).data, status=201)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    except Course.DoesNotExist:
        return Response({"error": f"Course '{course_code}' not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['DELETE'])
def drop_course(request, enrollment_id):
    username = request.query_params.get('username')
    if not username:
        return Response({"error": "Username is required."}, status=400)
    try:
        user       = User.objects.get(username=username)
        enrollment = Enrollment.objects.get(id=enrollment_id, student=user.profile)
        enrollment.delete()
        return Response({"message": "Course dropped successfully."}, status=200)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
    except Enrollment.DoesNotExist:
        return Response({"error": "Enrollment not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)