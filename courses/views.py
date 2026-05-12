from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import datetime
from django.utils.crypto import get_random_string
from .assignment_views import *
from .models import Course, Lesson, Enrollment, QuizQuestion, LessonProgress, UserActivity,QuizAttempt
from .quiz_views import *
from django.db.models import Avg,Count
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from axes.helpers import get_client_username
from axes.models import AccessAttempt
from .models import *
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape
from reportlab.lib.utils import ImageReader
import datetime
from django.contrib.auth.models import User
from .models import Cart, Payment
from django.contrib import messages
import uuid
from .forms import CourseForm

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

    course = get_object_or_404(
        Course,
        id=course_id
    )

    lessons = Lesson.objects.filter(
        course=course
    )

    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course
    ).count()

    progress = 0

    if total_lessons > 0:

        progress = int(
            (completed / total_lessons) * 100
        )

    # CHECK QUIZ PASSING

    quiz_passed = QuizAttempt.objects.filter(
        student=request.user,
        course=course,
        passed=True
    ).exists()

    return render(request, "courses/course_detail.html", {

        "course": course,

        "lessons": lessons,

        "progress": progress,

        "quiz_passed": quiz_passed
    })

# LESSON PLAYER PAGE (UDemy STYLE)

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

    course = get_object_or_404(
        Course,
        id=course_id
    )

    questions = QuizQuestion.objects.filter(
        course=course
    )

    # MAX QUIZ ATTEMPTS

    MAX_ATTEMPTS = 3

    attempt_count = QuizAttempt.objects.filter(
        student=request.user,
        course=course
    ).count()

    if attempt_count >= MAX_ATTEMPTS:

        return render(
            request,
            "courses/quiz_attempt_limit.html",
            {
                "course": course,
                "max_attempts": MAX_ATTEMPTS
            }
        )

    # LESSON COMPLETION CHECK

    lessons = Lesson.objects.filter(
        course=course
    )

    total_lessons = lessons.count()

    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course,
        completed=True
    ).count()

    if completed_lessons < total_lessons:

        return HttpResponse(
            "Complete all lessons before attempting the quiz."
        )

    # CHECK QUIZ QUESTIONS

    total_questions = questions.count()

    if total_questions == 0:

        return HttpResponse(
            "No quiz questions available for this course."
        )

    # QUIZ SUBMISSION

    if request.method == "POST":

        score = 0

        for q in questions:

            selected_answer = request.POST.get(
                f"question_{q.id}"
            )

            if (
                selected_answer and
                int(selected_answer) == q.correct_option
            ):

                score += 1

        # CALCULATE PERCENTAGE

        percentage = round(
            (score / total_questions) * 100,
            2
        )

        # PASSING CRITERIA

        passed = percentage >= 40

        # SAVE QUIZ ATTEMPT

        QuizAttempt.objects.create(

            student=request.user,

            course=course,

            score=score,

            total_questions=total_questions,

            percentage=percentage,

            passed=passed
        )

        # RESULT PAGE

        return render(
            request,
            "courses/quiz_result.html",
            {

                "course": course,

                "score": score,

                "total": total_questions,

                "percentage": percentage,

                "passed": passed
            }
        )

    # QUIZ PAGE

    return render(
        request,
        "courses/quiz.html",
        {

            "questions": questions,

            "course": course
        }
    )
@login_required
def quiz_history(request):

    attempts = QuizAttempt.objects.filter(
        student=request.user
    ).order_by('-attempted_at')

    return render(
        request,
        'courses/quiz_history.html',
        {
            'attempts': attempts
        }
    )
@login_required
def leaderboard(request):

    leaderboard_data = QuizAttempt.objects.values(
        'student__username'
    ).annotate(
        average_score=Avg('percentage'),
        quizzes_taken=Count('id')
    ).order_by('-average_score')[:10]

    total_students = leaderboard_data.count()

    top_score = 0

    if leaderboard_data:
        top_score = leaderboard_data[0]['average_score']

    return render(
        request,
        'courses/leaderboard.html',
        {
            'leaderboard_data': leaderboard_data,
            'total_students': total_students,
            'top_score': round(top_score, 2)
        }
    )

@login_required
def generate_certificate(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    user = request.user

    # LESSON CHECK

    lessons = Lesson.objects.filter(
        course=course
    )

    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
        student=user,
        lesson__course=course
    ).count()

    if total_lessons == 0 or completed < total_lessons:

        return redirect(
            "course_detail",
            course_id=course.id
        )

    # QUIZ PASS CHECK

    quiz_attempt = QuizAttempt.objects.filter(
        student=user,
        course=course,
        passed=True
    ).first()

    if not quiz_attempt:

        return redirect(
            "quiz",
            course_id=course.id
        )

    full_name = user.get_full_name()

    if not full_name:
        full_name = user.username

    completion_date = datetime.date.today().strftime(
        "%d %B %Y"
    )

    return render(
        request,
        "courses/certificate.html",
        {
            "course": course,
            "full_name": full_name,
            "completion_date": completion_date
        }
    )

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

    attempts = QuizAttempt.objects.filter(
        student=student
    )

    total_attempts = attempts.count()

    average_score = 0

    passed_count = attempts.filter(
        passed=True
    ).count()

    latest_attempt = attempts.first()

    if total_attempts > 0:

        average_score = round(

            sum(a.percentage for a in attempts) / total_attempts,

            2
        )

    pass_percentage = 0

    if total_attempts > 0:

        pass_percentage = round(

            (passed_count / total_attempts) * 100,

            2
        )

    # RECOMMENDATION ENGINE

    recommended_courses = Course.objects.none()

    if average_score < 40:

        recommended_courses = Course.objects.filter(
            level='Beginner'
        )[:3]

    elif average_score < 70:

        recommended_courses = Course.objects.filter(
            level='Intermediate'
        )[:3]

    else:

        recommended_courses = Course.objects.filter(
            level='Advanced'
        )[:3]

    return render(request, "courses/dashboard.html", {

        "total_courses": total_courses,

        "total_lessons": total_lessons,

        "completed_lessons": completed_lessons,

        "total_attempts": total_attempts,

        "average_score": average_score,

        "pass_percentage": pass_percentage,

        "latest_attempt": latest_attempt,

        "recommended_courses": recommended_courses
    })

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # REQUIRED VALIDATION

        if not first_name or not last_name:

            error = "First name and last name are required."

        elif password1 != password2:

            error = "Passwords do not match."

        elif User.objects.filter(username=username).exists():

            error = "Username already exists."

        else:

            user = User.objects.create_user(

                username=username,

                password=password1,

                first_name=first_name,

                last_name=last_name
            )

            user.save()

            return redirect("login")

    return render(request, "courses/register.html", {

        "error": error
    })

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # CHECK LOCKOUT

        attempts = AccessAttempt.objects.filter(username=username)

        if attempts.exists():
            attempt = attempts.first()

            if attempt.failures_since_start >= 5:
                messages.error(
                    request,
                    "Too many failed login attempts. Please try again later."
                )

                return render(request, "courses/login.html")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            if user.is_staff:
                return redirect("admin_dashboard")

            return redirect("dashboard")

        else:

            messages.error(request, "Invalid username or password")

            return render(request, "courses/login.html")

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

@login_required
def add_to_cart(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    # CHECK ALREADY PURCHASED

    already_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if already_enrolled:

        messages.warning(
            request,
            "You already purchased this course."
        )

        return redirect('course_list')

    # CHECK ALREADY IN CART

    already_in_cart = Cart.objects.filter(
        user=request.user,
        course=course
    ).exists()

    if already_in_cart:

        messages.info(
            request,
            "Course already exists in cart."
        )

        return redirect('cart')

    # ADD COURSE TO CART

    Cart.objects.create(
        user=request.user,
        course=course
    )

    messages.success(
        request,
        "Course added to cart successfully."
    )

    return redirect('cart')


@login_required
def cart_view(request):

    cart_items = Cart.objects.filter(
        user=request.user
    )

    total_price = sum(
        item.course.price
        for item in cart_items
    )

    gst = round(total_price * 0.18)

    final_total = total_price + gst

    return render(
        request,
        'courses/cart.html',
        {
            'cart_items': cart_items,
            'total_price': total_price,
            'gst': gst,
            'final_total': final_total
        }
    )

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(
        user=request.user
    )

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect('cart')

    total_price = sum(
        item.course.price
        for item in cart_items
    )

    gst = round(total_price * 0.18)

    final_total = total_price + gst

    if request.method == "POST":

        payment_method = request.POST.get(
            'payment_method'
        )

        for item in cart_items:

            Payment.objects.create(

                user=request.user,

                course=item.course,

                amount=item.course.price,

                payment_method=payment_method,

                status='Completed',

                transaction_id=get_random_string(12)
            )

            # AUTO ENROLL

            Enrollment.objects.get_or_create(

                student=request.user,

                course=item.course
            )

        # CLEAR CART

        cart_items.delete()

        messages.success(
            request,
            "Payment successful. Course unlocked."
        )

        return redirect('my_courses')

    return render(
        request,
        'courses/checkout.html',
        {
            'cart_items': cart_items,
            'total_price': total_price,
            'gst': gst,
            'final_total': final_total
        }
    )


@login_required
def remove_from_cart(request, cart_id):

    cart_item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    cart_item.delete()

    messages.success(
        request,
        "Course removed from cart."
    )

    return redirect('cart')

@login_required
def admin_courses(request):

    if not request.user.is_staff:

        return redirect('dashboard')

    courses = Course.objects.all()

    return render(
        request,
        'courses/admin_courses.html',
        {
            'courses': courses
        }
    )

@login_required
def add_course(request):

    if not request.user.is_staff:

        return redirect('dashboard')

    if request.method == 'POST':

        form = CourseForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course added successfully."
            )

            return redirect('admin_courses')

    else:

        form = CourseForm()

    return render(
        request,
        'courses/add_course.html',
        {
            'form': form
        }
    )

@login_required
def edit_course(request, course_id):

    if not request.user.is_staff:

        return redirect('dashboard')

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if request.method == 'POST':

        form = CourseForm(
            request.POST,
            request.FILES,
            instance=course
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course updated successfully."
            )

            return redirect('admin_courses')

    else:

        form = CourseForm(instance=course)

    return render(
        request,
        'courses/edit_course.html',
        {
            'form': form,
            'course': course
        }
    )

@login_required
def delete_course(request, course_id):

    if not request.user.is_staff:

        return redirect('dashboard')

    course = get_object_or_404(
        Course,
        id=course_id
    )

    course.delete()

    messages.success(
        request,
        "Course deleted successfully."
    )

    return redirect('admin_courses')