from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from courses import views
from courses.views import home
from courses.assignment_views import (
    assignment_list,
    assignment_detail,
    submit_assignment
)

from courses.views import (
    course_list,
    enroll_course,
    course_detail,
    my_courses,
    quiz_view,
    generate_certificate,
    dashboard,
    complete_lesson,
    lesson_detail
)
from courses.quiz_views import upload_quiz_csv

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('courses/', course_list, name='course_list'),
    path('enroll/<int:course_id>/', enroll_course, name='enroll_course'),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('my-courses/', my_courses, name='my_courses'),
    path('quiz/<int:course_id>/', quiz_view, name='quiz'),
    path(
    'certificate/<int:course_id>/',
    generate_certificate,
    name='generate_certificate'
),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('complete-lesson/<int:lesson_id>/', complete_lesson, name='complete_lesson'),
    path('lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('register/', views.register, name='register'),
    path("login/", views.login_view, name="login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path(
    'admin-courses/',
    views.admin_courses,
    name='admin_courses'
),

path(
    'add-course/',
    views.add_course,
    name='add_course'
),

path(
    'edit-course/<int:course_id>/',
    views.edit_course,
    name='edit_course'
),

path(
    'delete-course/<int:course_id>/',
    views.delete_course,
    name='delete_course'
),
    path(
    'course/<int:course_id>/assignments/',
    assignment_list,
    name='assignment_list'
),

path(
    'assignment/<int:assignment_id>/',
    assignment_detail,
    name='assignment_detail'
),

path(
    'assignment/<int:assignment_id>/submit/',
    submit_assignment,
    name='submit_assignment'
),
path(
    'upload-quiz-csv/',
    upload_quiz_csv,
    name='upload_quiz_csv'
),
path(
    'quiz-history/',
    views.quiz_history,
    name='quiz_history'
),
path(
    'leaderboard/',
    views.leaderboard,
    name='leaderboard'
),
path(
    'add-to-cart/<int:course_id>/',
    views.add_to_cart,
    name='add_to_cart'
),

path(
    'cart/',
    views.cart_view,
    name='cart'
),

path(
    'remove-from-cart/<int:cart_id>/',
    views.remove_from_cart,
    name='remove_from_cart'
),
path(
    'checkout/',
    views.checkout,
    name='checkout'
),

    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)