import requests
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from open_fitness_calculator.core.decorators import password_required, unauthenticated_required

from open_fitness_calculator.profiles.models import Profile
from open_fitness_calculator.profiles.forms import ProfileForm, GoalForm
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from django.views.generic import CreateView, FormView, RedirectView, UpdateView, DeleteView
from open_fitness_calculator.fitness_calculator_auth.forms import SignUpForm, SignInForm, \
    UpdateUserCredentialsForm, UpdateUserPasswordForm, RequirePasswordForm
from open_fitness_calculator.settings import ALLOWED_HOSTS, DEBUG


@method_decorator(unauthenticated_required, name="dispatch")
class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("profile details")
    template_name = "fitness_calculator_auth/sign_up.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


@method_decorator(unauthenticated_required, name="dispatch")
class SignInView(FormView):
    form_class = SignInForm
    success_url = reverse_lazy("home")
    template_name = "fitness_calculator_auth/sign_in.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super(SignInView, self).form_valid(form)


class SignOutView(RedirectView):
    url = reverse_lazy("sign in")

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return super(SignOutView, self).get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class RequirePasswordView(FormView):
    form_class = RequirePasswordForm
    template_name = "fitness_calculator_auth/require_password.html"
    __redirect_mapper = {
        "GET": lambda url: requests.get(url),
        "POST": lambda url: requests.post(url),
    }

    def get_form_kwargs(self):
        kwargs = super(RequirePasswordView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        self.request.session["password_not_required_auth"] = True
        next_url = self.request.GET.get(REDIRECT_FIELD_NAME) or "/"
        return redirect(next_url)


@method_decorator(login_required, name="dispatch")
@method_decorator(password_required, name="dispatch")
class UserCredentialsUpdateView(UpdateView):
    form_class = UpdateUserCredentialsForm
    success_url = reverse_lazy("profile details")
    template_name = "fitness_calculator_auth/update_user_credentials.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        self.extra_context = {"profile": self.request.user.profile}
        return super(UserCredentialsUpdateView, self).get_context_data(**kwargs)


@method_decorator(login_required, name="dispatch")
@method_decorator(password_required, name="dispatch")
class UserPasswordUpdateView(FormView):
    form_class = UpdateUserPasswordForm
    success_url = reverse_lazy("update user credentials")
    template_name = "fitness_calculator_auth/update_user_password.html"

    def get_context_data(self, **kwargs):
        self.extra_context = {"profile": self.request.user.profile}
        return super(UserPasswordUpdateView, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserPasswordUpdateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(UserPasswordUpdateView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(password_required, name="dispatch")
class UserDeleteView(DeleteView):
    object = None
    model = FitnessCalculatorUser
    template_name = "profile/profile_delete.html"
    success_url = reverse_lazy("sign in")

    def get_object(self, queryset=None):
        self.kwargs["pk"] = self.request.user.pk
        return super(UserDeleteView, self).get_object()

    def get_context_data(self, **kwargs):
        profile = get_object_or_404(Profile, pk=self.get_object().pk)
        self.extra_context = {
            "form": ProfileForm(
                initial=profile.__dict__,
                disable_fields=True,
            ),
            "goals_form": GoalForm(
                initial=profile.goal.__dict__,
                disable_fields=True,
            ),
            "profile": profile,
        }
        return super(UserDeleteView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.form_valid(None)
