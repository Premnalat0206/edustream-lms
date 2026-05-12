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