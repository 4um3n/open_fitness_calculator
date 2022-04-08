from django.urls import path
from open_fitness_calculator.profiles.views import ProfileUpdateView, RequestBecomingStaffView, StaffView

urlpatterns = [
    path(
        "details/",
        ProfileUpdateView.as_view(),
        name="profile details"
    ),
    path(
        "request-becoming-staff/",
        RequestBecomingStaffView.as_view(),
        name="profile become staff",
    ),
    path(
        "staff/<int:profile_pk>",
        StaffView.as_view(),
        name="staff",
    ),
]
