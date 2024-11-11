import logging
from typing import TypeVar, cast

from django.contrib.auth.models import AnonymousUser
from django.db import models
from guardian.models import GroupObjectPermissionBase, UserObjectPermissionBase
from guardian.shortcuts import get_objects_for_user
from users.models import ExampleUser


logger = logging.getLogger(__file__)

T = TypeVar("T", bound="Question")
"""
Here we have an hieararchy model for Question as parent and Choice as a children.
Question1:
    - Choice1
    - Choice2
Question2:
    - Choice3
    - Choice4

We assyme that Choice permissions is mirrored from Question and should be automatically propagate
"""


class QuestionManager(models.Manager["Question"]):
    def with_permission(self, user: ExampleUser | AnonymousUser, perm_code_name: str) -> models.QuerySet["Question"]:
        queryset = cast(
            models.QuerySet[Question],
            get_objects_for_user(user, perm_code_name, klass=Question, accept_global_perms=False),
        )
        return queryset


class Question(models.Model):  # type: ignore[django-manager-missing]
    objects: QuestionManager = QuestionManager()

    value = models.TextField(max_length=200)


class QuestionChoiceManager(models.Manager["Choice"]):
    def with_question_permission(
        self, user: ExampleUser | AnonymousUser, perm_code_name: str
    ) -> models.QuerySet["Choice"]:
        questions_queryset = cast(
            models.QuerySet[Question],
            get_objects_for_user(user, perm_code_name, klass=Question, accept_global_perms=False),
        )
        return self.filter(question__in=questions_queryset)


class Choice(models.Model):
    objects: QuestionChoiceManager = QuestionChoiceManager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    value = models.TextField(max_length=200)


class QuestionUserObjectPermission(UserObjectPermissionBase):  # type: ignore[misc]
    content_object: 'models.ForeignKey[Question]' = models.ForeignKey(Question, on_delete=models.CASCADE)


class QuestionGroupObjectPermission(GroupObjectPermissionBase):  # type: ignore[misc]
    content_object: 'models.ForeignKey[Question]' = models.ForeignKey(Question, on_delete=models.CASCADE)
