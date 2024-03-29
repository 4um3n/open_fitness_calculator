from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """
    ModelBacked that allows authentication
    with either a username or an email address.
    """
    __USER_MODEL = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs):
        username = username or ""

        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}

        try:
            user = self.__USER_MODEL.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except self.__USER_MODEL.DoesNotExist:
            return None

