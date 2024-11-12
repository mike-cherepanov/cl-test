# questions/tasks.py

from __future__ import absolute_import, unicode_literals

import random
from logging import getLogger

from celery import shared_task
from django.db import transaction
from django.utils.crypto import get_random_string
from guardian.shortcuts import assign_perm
from users.models import ExampleUser

from .models import Choice, Question


logger = getLogger(__file__)


@shared_task  # type: ignore
def create_random_question() -> str:
    with transaction.atomic():
        logger.info('Called create_random_question')
        # Create a new Question
        question_text = f"Random Question {get_random_string(10)}"
        question = Question.objects.create(value=question_text)

        # Create a random number of Choices (between 2 and 5)
        num_choices = random.randint(2, 5)
        for _ in range(num_choices):
            choice_text = f"Choice {get_random_string(5)}"
            Choice.objects.create(question=question, value=choice_text)

        # Assign permissions to a random User
        users = ExampleUser.objects.all()
        if users.exists():
            user = random.choice(users)
            assign_perm('view_question', user, question)
            assign_perm('change_question', user, question)
            assign_perm('delete_question', user, question)

        return f"Question '{question_text}' created with {num_choices} choices."
