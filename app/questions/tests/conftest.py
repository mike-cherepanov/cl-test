from typing import Any, Callable

import pytest
from users.models import ExampleUser

from questions.models import Choice, Question


type CreateUser = Callable[[str], ExampleUser]
type CreateQuestion = Callable[[str], Question]


@pytest.fixture
def create_user(db: Any) -> CreateUser:
    def make_by_username(username: str) -> ExampleUser:
        return ExampleUser.objects.create_user(username=username, password=username)

    return make_by_username


@pytest.fixture
def user_1(create_user: CreateUser) -> ExampleUser:
    return create_user('user_1')


@pytest.fixture
def user_2(create_user: CreateUser) -> ExampleUser:
    return create_user('user_2')


@pytest.fixture
def create_question(db: Any) -> CreateQuestion:
    def make_by_question_value(value: str) -> Question:
        question: Question = Question.objects.create(value=value)
        question.choices.bulk_create(
            [
                Choice(question=question, value=f'{value}_1'),
                Choice(question=question, value=f'{value}_2'),
                Choice(question=question, value=f'{value}_3'),
            ]
        )
        return question

    return make_by_question_value
