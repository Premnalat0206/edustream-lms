from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Course, Assignment, AssignmentSubmission
from .forms import AssignmentSubmissionForm


@login_required
def assignment_list(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    assignments = course.assignments.all()

    context = {
        'course': course,
        'assignments': assignments
    }

    return render(
        request,
        'courses/assignment_list.html',
        context
    )


@login_required
def assignment_detail(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()

    context = {
        'assignment': assignment,
        'submission': submission
    }

    return render(
        request,
        'courses/assignment_detail.html',
        context
    )


@login_required
def submit_assignment(request, assignment_id):

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id
    )

    existing_submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=request.user
    ).exists()

    if existing_submission:

        messages.warning(
            request,
            'You already submitted this assignment.'
        )

        return redirect(
            'assignment_detail',
            assignment_id=assignment.id
        )

    if request.method == 'POST':

        form = AssignmentSubmissionForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            submission = form.save(commit=False)

            submission.assignment = assignment

            submission.student = request.user

            submission.save()

            messages.success(
                request,
                'Assignment submitted successfully.'
            )

            return redirect(
                'assignment_detail',
                assignment_id=assignment.id
            )

    else:

        form = AssignmentSubmissionForm()

    context = {
        'assignment': assignment,
        'form': form
    }

    return render(
        request,
        'courses/submit_assignment.html',
        context
    )