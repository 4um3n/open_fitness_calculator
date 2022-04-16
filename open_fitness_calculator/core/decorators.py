from functools import wraps

import requests
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME


def password_required(view_function, redirect_field_name=REDIRECT_FIELD_NAME):
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('password_not_required_auth', False) or request.method == "POST":
            request.session["password_not_required_auth"] = False
            return view_function(request, *args, **kwargs)

        request.session["nex_url_method"] = request.method
        return HttpResponseRedirect('%s?%s=%s' % (
            reverse('password required'),
            redirect_field_name,
            request.get_full_path(),
        ))

    return wraps(view_function)(_wrapped_view)


def unauthenticated_required(view_function):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return view_function(request, *args, **kwargs)

    return wraps(view_function)(_wrapped_view)


