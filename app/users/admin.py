# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ExampleUser


admin.site.register(ExampleUser, UserAdmin)
