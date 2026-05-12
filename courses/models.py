from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Instructor(models.Model):

    name = models.CharField(max_length=100)

    expertise = models.CharField(
        max_length=200
    )

    bio = models.TextField()

    image = models.ImageField(
        upload_to='instructors/'
    )

    def __str__(self):
        return self.name


class Course(models.Model):

    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default= None
    )

    image = models.ImageField(
        upload_to="course_images/",
        blank=True,
        null=True
    )

    duration = models.CharField(
        max_length=50,
        default="10 Hours"
    )

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='Beginner'
    )

    rating = models.FloatField(
        default=4.5
    )

    students = models.IntegerField(
        default=1200
    )

    price = models.IntegerField(
        default=499
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Assignment(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    due_date = models.DateTimeField()

    total_marks = models.PositiveIntegerField(default=100)

    instructions = models.FileField(
        upload_to='assignment_instructions/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_overdue(self):
        return timezone.now() > self.due_date

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    submission_file = models.FileField(
        upload_to='assignment_submissions/'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    marks_obtained = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    feedback = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f'{self.student.username} - {self.assignment.title}'
    

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    video_url = models.CharField(max_length=500)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title
    
class QuizQuestion(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)

    OPTION_CHOICES = (
        (1, "Option 1"),
        (2, "Option 2"),
        (3, "Option 3"),
        (4, "Option 4"),
    )

    correct_option = models.IntegerField(choices=OPTION_CHOICES)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.course.title} - {self.question[:50]}"
    
class QuizAttempt(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    score = models.IntegerField()

    total_questions = models.IntegerField()

    percentage = models.FloatField()

    passed = models.BooleanField(default=False)

    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        return f'{self.student.username} - {self.course.title}'
    
class LessonProgress(models.Model):

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"