from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, RedirectView, FormView
from open_fitness_calculator.profiles.models import Profile
from open_fitness_calculator.profiles.forms import ProfileForm, GoalForm, StaffForm


@method_decorator(login_required, name="dispatch")
class ProfileUpdateView(UpdateView):
    form_class = ProfileForm
    model = Profile
    template_name = "profile/profile_update.html"
    success_url = reverse_lazy("profile details")

    def get_object(self, queryset=None):
        self.kwargs["pk"] = self.request.user.pk
        return super(ProfileUpdateView, self).get_object()

    def get_context_data(self, **kwargs):
        profile = self.get_object()
        self.extra_context = {"goals_form": GoalForm(initial=profile.goal.__dict__)}
        return super(ProfileUpdateView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        goal_form = GoalForm(request.POST, instance=self.get_object().goal)
        if goal_form.is_valid():
            goal_form.save()
            return super(ProfileUpdateView, self).post(request, *args, **kwargs)
        return super(ProfileUpdateView, self).form_invalid(goal_form)


@method_decorator(login_required, name="dispatch")
class RequestBecomingStaffView(RedirectView):
    url = reverse_lazy("update user credentials")

    def get(self, request, *args, **kwargs):
        profile = self.request.user.profile
        profile.request_becoming_staff()
        return super(RequestBecomingStaffView, self).get(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class StaffView(FormView):
    form_class = StaffForm
    model = Profile
    pk_url_kwarg = "profile_pk"
    template_name = "profile/profile_staff.html"
    success_url = reverse_lazy("staff", kwargs={"profile_pk": 0})

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        profile_pk = self.request.user.profile.pk
        staff = self.model.objects.filter(is_staff=True).exclude(pk=profile_pk)
        requested_staff = self.model.objects.filter(is_staff=False, requested_staff=True).exclude(pk=profile_pk)

        self.extra_context = {
            "profiles_staff": [],
            "profiles_requested_staff": [],
        }

        for profile_staff in staff:
            self.initial = profile_staff.__dict__
            self.extra_context["profiles_staff"].append((profile_staff, self.get_form()))

        for profile_requested_staff in requested_staff:
            self.initial = profile_requested_staff.__dict__
            self.extra_context["profiles_requested_staff"].append((profile_requested_staff, self.get_form()))

        return self.extra_context

    def post(self, request, *args, **kwargs):
        is_staff = not self.get_object().is_staff
        self.model.objects.filter(pk=self.get_object().pk).update(is_staff=is_staff)
        return self.render_to_response(self.get_context_data())

    def get_form_kwargs(self):
        return {
            "initial": self.initial.copy(),
        }
