import pytest
from guardian.shortcuts import assign_perm
from questions.models import Choice, Question
from users.models import ExampleUser


@pytest.fixture
def user_1() -> ExampleUser:
    return ExampleUser.objects.create(username='user_1')


@pytest.fixture
def question_1() -> Question:
    question = Question(value='question_1')
    question.save()
    for i in range(3):
        question.choices.add(Choice(value=str(i + 1)), bulk=False)
    return question


@pytest.fixture
def question_2() -> Question:
    question = Question(value='question_2')
    question.save()
    for i in range(3):
        question.choices.add(Choice(value=str(i + 1)), bulk=False)
    return question


@pytest.mark.django_db
def test_manager_return_only_by_permission(user_1: ExampleUser, question_1: Question, question_2: Question) -> None:
    assert Question.objects.with_permission(user_1, 'change_question').count() == 0
    assign_perm('change_question', user_1, question_1)
    assert Question.objects.with_permission(user_1, 'change_question').first() == question_1
    assert Question.objects.with_permission(user_1, 'change_question').count() == 1
