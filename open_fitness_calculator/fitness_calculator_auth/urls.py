from django.urls import path
from open_fitness_calculator.fitness_calculator_auth.views import SignUpView, SignInView, SignOutView, \
    UserCredentialsUpdateView, UserDeleteView, UserPasswordUpdateView, OldPasswordView

urlpatterns = [
    path('sign-up/', SignUpView.as_view(), name="sign up"),
    path('sign-in/', SignInView.as_view(), name="sign in"),
    path('sign-out/', SignOutView.as_view(), name="sign out"),
    path(
        'confirm-old-password/',
        OldPasswordView.as_view(),
        name="confirm old password"
    ),
    path(
        'user-update-credentials/',
        UserCredentialsUpdateView.as_view(),
        name="update user credentials"
    ),
    path(
        "user-update-password/",
        UserPasswordUpdateView.as_view(),
        name="update user password"
    ),
    path(
        "user-delete/",
        UserDeleteView.as_view(),
        name="user delete"
    ),
]

