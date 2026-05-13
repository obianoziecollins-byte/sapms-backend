from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    student_id = models.CharField(max_length=15, unique=True)
    DEPARTMENT_CHOICES = [('Computer Science', 'Computer Science')]
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES,
                                  default='Computer Science', editable=False)
    LEVEL_CHOICES = [(100,'100'),(200,'200'),(300,'300'),(400,'400')]
    level = models.IntegerField(choices=LEVEL_CHOICES, default=100)
    SPECIALIZATION_CHOICES = [
        ('AI','Artificial Intelligence'),
        ('ML','Machine Learning'),
        ('CG','Computer Graphics'),
        ('CY','Cyber Security'),
        ('SE','Software Engineering'),
        ('IT','Information Technology'),
        ('DS','Data Science'),
        ('CC','Cloud Computing'),
    ]
    specialization = models.CharField(max_length=2, choices=SPECIALIZATION_CHOICES)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_on_probation = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        try:
            self.is_on_probation = float(self.cgpa) <= 1.50
        except (TypeError, ValueError):
            self.is_on_probation = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"


class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    CREDIT_CHOICES = [(1,'1'),(2,'2'),(3,'3')]
    credit_units = models.IntegerField(default=3, choices=CREDIT_CHOICES,
                                       validators=[MinValueValidator(1), MaxValueValidator(3)])
    is_mandatory = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course_code}: {self.title}"


class Prerequisite(models.Model):
    """
    Stores prerequisite rules. Each row means:
      'course' cannot be enrolled in unless 'required_course'
      has been completed with at least 'min_grade'.

    Add entries through the Django admin panel.
    Example:
      course=CSC 201, required_course=CSC 101, min_grade=E
      course=CSC 301, required_course=CSC 201, min_grade=E
    """
    # null=True and blank=True
    course = models.ForeignKey(
        'Course', 
        on_delete=models.CASCADE, 
        related_name='unlocks',
        null=True, 
        blank=True
    )
    required_course = models.ForeignKey(
        'Course', 
        on_delete=models.CASCADE, 
        related_name='prerequisites',
        null=True, 
        blank=True
    )
    GRADE_CHOICES = [('A','A'),('B','B'),('C','C'),('D','D'),('E','E')]
    min_grade = models.CharField(max_length=1, choices=GRADE_CHOICES, default='E')

    class Meta:
        unique_together = ('course', 'required_course')
        
        def __str__(self):
            return f"{self.course.course_code} requires {self.required_course.course_code} (min: {self.min_grade})"


class Enrollment(models.Model):
    SEMESTER_CHOICES = [('1st','1st Semester'),('2nd','2nd Semester')]
    GRADE_CHOICES = [
        ('IP','In Progress'),
        ('A','A'),('B','B'),('C','C'),('D','D'),('E','E'),('F','F')
    ]
    student  = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='enrollments')
    course   = models.ForeignKey('Course', on_delete=models.CASCADE)
    grade    = models.CharField(max_length=2, choices=GRADE_CHOICES, default='IP', blank=True)
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES, default='1st')

    class Meta:
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f"{self.student.student_id} - {self.course.course_code} ({self.semester})"


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.get_or_create(
            user=instance,
            defaults={'student_id': f'TEMP-{instance.pk}'}
        )