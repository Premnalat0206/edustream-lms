import csv
import io

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .forms import QuizCSVUploadForm
from .models import QuizQuestion


@staff_member_required
def upload_quiz_csv(request):

    if request.method == 'POST':

        form = QuizCSVUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            course = form.cleaned_data['course']

            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):

                messages.error(
                    request,
                    'Please upload a CSV file.'
                )

                return redirect('upload_quiz_csv')

            data = csv_file.read().decode('utf-8')

            io_string = io.StringIO(data)

            next(io_string)

            for row in csv.reader(io_string):

                QuizQuestion.objects.create(

                    course=course,

                    question=row[0],

                    option1=row[1],

                    option2=row[2],

                    option3=row[3],

                    option4=row[4],

                    correct_option=int(row[5])

                )

            messages.success(
                request,
                'Quiz questions uploaded successfully.'
            )

            return redirect('upload_quiz_csv')

    else:

        form = QuizCSVUploadForm()

    context = {
        'form': form
    }

    return render(
        request,
        'courses/upload_quiz_csv.html',
        context
    )