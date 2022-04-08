from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, FormView, RedirectView, UpdateView, DeleteView
from open_fitness_calculator.fitness_calculator_auth.forms import SignUpForm, SignInForm, UpdateUserCredentialsForm, \
    UpdateUserPasswordForm, OldPasswordForm
from open_fitness_calculator.fitness_calculator_auth.models import FitnessCalculatorUser
from open_fitness_calculator.profiles.forms import ProfileForm, GoalForm
from open_fitness_calculator.profiles.models import Profile


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("profile details")
    template_name = "fitness_calculator_auth/sign_up.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        return super(SignUpView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        Profile(user=user).save()
        login(self.request, user)
        return redirect(self.success_url)


class SignInView(FormView):
    form_class = SignInForm
    success_url = reverse_lazy("home")
    template_name = "fitness_calculator_auth/sign_in.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        return super(SignInView, self).get(request, *args, **kwargs)

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
class OldPasswordView(FormView):
    form_class = OldPasswordForm
    success_url = reverse_lazy("update user credentials")
    template_name = "fitness_calculator_auth/old_password.html"

    def get_form_kwargs(self):
        kwargs = super(OldPasswordView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@method_decorator(login_required, name="dispatch")
class UserCredentialsUpdateView(UpdateView):
    form_class = UpdateUserCredentialsForm
    success_url = reverse_lazy("profile details")
    template_name = "fitness_calculator_auth/update_user_credentials.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        self.extra_context = {
            "profile": self.request.user.profile
        }
        return super(UserCredentialsUpdateView, self).get_context_data(**kwargs)


@method_decorator(login_required, name="dispatch")
class UserPasswordUpdateView(FormView):
    form_class = UpdateUserPasswordForm
    success_url = reverse_lazy("update user credentials")
    template_name = "fitness_calculator_auth/update_user_password.html"

    def get_context_data(self, **kwargs):
        self.extra_context = {
            "profile": self.request.user.profile
        }
        return super(UserPasswordUpdateView, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserPasswordUpdateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(UserPasswordUpdateView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class UserDeleteView(DeleteView):
    model = FitnessCalculatorUser
    template_name = "profile/profile_delete.html"
    success_url = reverse_lazy("sign in")

    def get_object(self, queryset=None):
        self.kwargs["pk"] = self.request.user.pk
        return super(UserDeleteView, self).get_object()

    def get_context_data(self, **kwargs):
        profile = Profile.objects.get(pk=self.get_object().pk)
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
