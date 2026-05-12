from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import QuizAttempt

from .models import (
    Course,
    Lesson,
    QuizQuestion,
    Category,
    Instructor
)


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    pass


@admin.register(Instructor)
class InstructorAdmin(ImportExportModelAdmin):

    list_display = (
        'name',
        'expertise'
    )


@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):

    list_display = (
        'title',
        'instructor',
        'category',
        'level',
        'rating',
        'price'
    )

    search_fields = ('title',)

    list_filter = ('level', 'category')


# =========================
# LESSON IMPORT RESOURCE
# =========================

class LessonResource(resources.ModelResource):

    course = fields.Field(
        column_name='course',
        attribute='course',
        widget=ForeignKeyWidget(Course, 'title')
    )

    class Meta:
        model = Lesson


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):

    resource_class = LessonResource

    list_display = (
        'title',
        'course'
    )


@admin.register(QuizQuestion)
class QuizQuestionAdmin(ImportExportModelAdmin):
    pass

@admin.register(QuizAttempt)
class QuizAttemptAdmin(ImportExportModelAdmin):

    list_display = (
        'student',
        'course',
        'score',
        'percentage',
        'passed',
        'attempted_at'
    )

    list_filter = (
        'passed',
        'course'
    )

    search_fields = (
        'student__username',
        'course__title'
    )