from django.contrib import messages
from django.shortcuts import redirect


def custom_lockout_response(request, credentials=None, *args, **kwargs):
    messages.error(
        request,
        "Too many failed login attempts. Please try again later."
    )
    return redirect('/login/')