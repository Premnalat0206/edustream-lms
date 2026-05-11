from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import datetime
from .models import Course, Lesson, Enrollment, QuizQuestion, LessonProgress, UserActivity

# COURSE LIST + SEARCH
@login_required
def course_list(request):

    query = request.GET.get('q')

    if query:
        courses = Course.objects.filter(title__icontains=query)
    else:
        courses = Course.objects.all()

    course_progress = {}

    for course in courses:

        lessons = Lesson.objects.filter(course=course)
        total = lessons.count()

        completed = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course
        ).count()

        progress = 0
        if total > 0:
            progress = int((completed / total) * 100)

        course_progress[course.id] = progress

    return render(request, "courses/course_list.html", {
        "courses": courses,
        "course_progress": course_progress
    })

# ENROLL COURSE
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    return redirect("my_courses")


# COURSE DETAIL + PROGRESS
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    lessons = Lesson.objects.filter(course=course)

    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course
    ).count()

    progress = 0
    if total_lessons > 0:
        progress = int((completed / total_lessons) * 100)

    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "progress": progress
    })


# LESSON PLAYER PAGE (UDemy STYLE)
@login_required
@login_required
def lesson_detail(request, lesson_id):

    lesson = get_object_or_404(Lesson, id=lesson_id)

    course = lesson.course

    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        return redirect("course_detail", course_id=course.id)

    lessons = Lesson.objects.filter(course=course).order_by("id")

    return render(request, "courses/lesson_detail.html", {
        "lesson": lesson,
        "course": course,
        "lessons": lessons
    })
    
  

# MARK LESSON COMPLETE
@login_required
def complete_lesson(request, lesson_id):

    lesson = get_object_or_404(Lesson, id=lesson_id)

    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    progress.completed = True
    progress.completed_at = datetime.datetime.now()
    progress.save()

    UserActivity.objects.create(
        user=request.user,
        action=f"Completed lesson: {lesson.title}"
    )

    return redirect("course_detail", course_id=lesson.course.id)
    



# MY COURSES
@login_required
def my_courses(request):

    enrollments = Enrollment.objects.filter(student=request.user)

    return render(request, "courses/my_courses.html", {
        "enrollments": enrollments
    })


# QUIZ VIEW
@login_required
def quiz_view(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    questions = QuizQuestion.objects.filter(course=course)

    lessons = Lesson.objects.filter(course=course)
    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
    student=request.user,
    lesson__course=course,
    completed=True
    ).count()

    if completed < total_lessons:
        return HttpResponse("Complete all lessons before attempting the quiz.")

    if request.method == "POST":

        score = 0
        total = questions.count()

        for q in questions:

            answer = request.POST.get(f"question_{q.id}")

            if answer and int(answer) == q.correct_option:
                score += 1

        return render(request, "courses/quiz_result.html", {
            "score": score,
            "total": total
        })

    return render(request, "courses/quiz.html", {
        "questions": questions,
        "course": course
    })

# GENERATE CERTIFICATE
@login_required
def generate_certificate(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    user = request.user

    lessons = Lesson.objects.filter(course=course)
    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
        student=user,
        lesson__course=course
    ).count()

    if completed < total_lessons:
        return redirect("course_detail", course_id=course.id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'

    p = canvas.Canvas(response)

    # PAGE SIZE
    width = 800
    height = 600

    # BORDER
    p.setLineWidth(6)
    p.rect(30, 30, 740, 540)

    p.setLineWidth(2)
    p.rect(50, 50, 700, 500)

    # TITLE
    p.setFont("Helvetica-Bold", 40)
    p.drawCentredString(400, 500, "CERTIFICATE")

    p.setFont("Helvetica", 25)
    p.drawCentredString(400, 460, "OF COMPLETION")

    # BODY TEXT
    p.setFont("Helvetica", 16)
    p.drawCentredString(400, 400, "This certificate is proudly presented to")

    # STUDENT NAME
    p.setFont("Helvetica-Bold", 28)
    p.drawCentredString(400, 360, user.username)

    p.setFont("Helvetica", 16)
    p.drawCentredString(400, 320, "for successfully completing the course")

    # COURSE NAME
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(400, 290, course.title)

    # DATE
    date = datetime.date.today()

    p.setFont("Helvetica", 14)
    p.drawCentredString(400, 240, f"Date: {date}")

    # SIGNATURE
    p.line(300, 180, 500, 180)
    p.setFont("Helvetica", 12)
    p.drawCentredString(400, 160, "Instructor Signature")

    # FOOTER
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(400, 120, "EduStream Learning Platform")

    p.showPage()
    p.save()

    return response

# DASHBOARD
@login_required
def dashboard(request):

    student = request.user

    enrollments = Enrollment.objects.filter(student=student)
    total_courses = enrollments.count()

    total_lessons = Lesson.objects.count()

    completed_lessons = LessonProgress.objects.filter(
        student=student
    ).count()

    return render(request, "courses/dashboard.html", {
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons
    })

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(request, "courses/register.html", {"form": form})

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            if user.is_staff:
                return redirect("admin_dashboard")
            else:
                return redirect("dashboard")

        else:
            return render(request, "courses/login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "courses/login.html")

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect("dashboard")

    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()

    activities = UserActivity.objects.order_by("-timestamp")[:10]

    return render(request, "courses/admin_dashboard.html", {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "activities": activities
    })

def home(request):

    courses = Course.objects.all()[:6]

    return render(request, "courses/home.html", {
        "courses": courses
    })