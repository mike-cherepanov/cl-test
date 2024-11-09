from django.contrib.auth.models import AbstractUser
from guardian.mixins import GuardianUserMixin


# Create your models here.
class ExampleUser(AbstractUser, GuardianUserMixin):  # type: ignore[misc,django-manager-missing]
    ...
