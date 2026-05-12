from django import forms
from .models import AssignmentSubmission
from .models import Course


class AssignmentSubmissionForm(forms.ModelForm):

    class Meta:
        model = AssignmentSubmission

        fields = ['submission_file']

        widgets = {
            'submission_file': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }

class QuizCSVUploadForm(forms.Form):

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    csv_file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [

            'title',

            'description',

            'category',

            'instructor',

            'image',

            'duration',

            'level',

            'rating',

            'students',

            'price'
        ]

        widgets = {

            'title': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5
                }
            ),

            'category': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'instructor': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'image': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'duration': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'level': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'rating': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'students': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }