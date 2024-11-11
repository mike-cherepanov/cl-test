from typing import cast

import pytest
from django.urls import reverse
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APIClient
from users.models import ExampleUser

from questions.models import Choice

from .conftest import CreateQuestion


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_get_list_request_auth(
    api_client: APIClient,
    user_1: ExampleUser,
) -> None:
    # allow access to view /questions collection
    assign_perm('questions.view_question', user_1)
    url = reverse('questions-list')

    assert api_client.get(url).status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(user_1)
    assert api_client.get(url).status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    'permission,count',
    [
        ('questions.view_question', 1),
        ('questions.change_question', 0),
        ('questions.add_question', 0),
        ('questions.delete_question', 0),
    ],
)
# test that user can list questions and receive only questions with granted read permission
def test_user_can_list_only_questions_with_read_permissions(
    api_client: APIClient,
    user_1: ExampleUser,
    user_2: ExampleUser,
    create_question: CreateQuestion,
    permission: str,
    count: str,
) -> None:
    assign_perm('questions.view_question', user_1)
    assign_perm('questions.view_question', user_2)

    question = create_question('question')
    assign_perm(permission, user_1, question)

    url = reverse('questions-list')
    api_client.force_authenticate(user_2)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0, response.data

    api_client.force_authenticate(user_1)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == count
    if count:
        assert response.data['results'][0]['id'] == question.id


@pytest.mark.parametrize(
    'permission,status_code',
    [
        ('questions.view_question', status.HTTP_200_OK),
        ('questions.change_question', status.HTTP_403_FORBIDDEN),
        ('questions.add_question', status.HTTP_403_FORBIDDEN),
        ('questions.delete_question', status.HTTP_403_FORBIDDEN),
    ],
)
#  test that user can get question details granted read permission for that question only
def test_user_can_get_questions_details_only_with_read_permissions(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
    permission: str,
    status_code: int,
) -> None:
    assign_perm('questions.view_question', user_1)

    question = create_question('question_1')
    assign_perm(permission, user_1, question)

    url = reverse('questions-detail', args=(question.id,))
    api_client.force_authenticate(user_1)
    response = api_client.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'permission,status_code',
    [
        ('questions.view_question', status.HTTP_403_FORBIDDEN),
        ('questions.change_question', status.HTTP_200_OK),
        ('questions.add_question', status.HTTP_403_FORBIDDEN),
        ('questions.delete_question', status.HTTP_403_FORBIDDEN),
    ],
)
# test that user can change question `value` with granted change permission only
def test_user_can_change_question_with_granted_change_permission(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
    permission: str,
    status_code: int,
) -> None:
    assign_perm('questions.change_question', user_1)
    question = create_question('question_1')
    assign_perm(permission, user_1, question)

    url = reverse('questions-detail', args=(question.id,))
    api_client.force_authenticate(user_1)

    # check full update
    response = api_client.put(url, data={'value': 'test'})
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert response.data['value'] == 'test', response.data

    # check partial update
    response = api_client.patch(url, data={'value': 'test'})
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert response.data['value'] == 'test', response.data


# test that user can create new question and it will be granted for full access to user
def test_user_can_create_new_questions(api_client: APIClient, user_1: ExampleUser) -> None:
    assign_perm('questions.view_question', user_1)
    assign_perm('questions.add_question', user_1)

    url = reverse('questions-list')
    api_client.force_authenticate(user_1)
    assert api_client.get(url).data['count'] == 0

    response = api_client.post(url, data={'value': "test"})
    assert response.status_code == status.HTTP_201_CREATED, response.data

    response = api_client.get(url)
    assert response.data['count'] == 1
    question = response.data['results'][0]
    assert question['value'] == 'test'

    url = reverse('questions-detail', args=(question['id'],))
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == question['id']


def test_user_can_delete_allowed_questions(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
) -> None:
    assign_perm('questions.view_question', user_1)
    assign_perm('questions.delete_question', user_1)
    question_1 = create_question('question_1')
    question_2 = create_question('question_2')
    api_client.force_authenticate(user_1)

    assign_perm('questions.delete_question', user_1, question_1)

    # check for not allowed question
    url = reverse('questions-detail', args=(question_2.id,))
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # check for allowed question
    url = reverse('questions-detail', args=(question_1.id,))
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # test that user can delete question with granted delete permission only


#     user can view question choices in the questions/{question_id}/choices/{choice_id} response body
# for question with granted read permission
def test_user_can_get_choice_details_for_allowed_questions(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
) -> None:
    assign_perm('questions.view_question', user_1)
    question_1 = create_question('question_1')
    question_2 = create_question('question_2')
    assign_perm('questions.view_question', user_1, question_1)
    api_client.force_authenticate(user_1)

    # not allowed choice from not allowed question
    choice_2 = cast(Choice, question_2.choices.first())
    url = reverse('question-choices-detail', args=(choice_2.question.id, choice_2.id))
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # choice from allowed to read question
    choice = cast(Choice, question_1.choices.first())
    url = reverse('question-choices-detail', args=(choice.question.id, choice.id))
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['question'] == question_1.id, response.data
    assert response.data['id'] == choice.id, response.data


# for question with granted change permission
#     user can change question choices `value`
def test_user_can_change_allowed_question_choice(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
) -> None:
    api_client.force_authenticate(user_1)
    assign_perm('questions.view_question', user_1)
    assign_perm('questions.change_question', user_1)
    question_1 = create_question('question_1')
    question_2 = create_question('question_2')

    assign_perm('questions.view_question', user_1, question_1)
    assign_perm('questions.change_question', user_1, question_1)

    # can't change choice for not allowed question
    choice_2: Choice = cast(Choice, question_2.choices.first())
    url = reverse('question-choices-detail', args=(choice_2.question.id, choice_2.id))
    assert api_client.put(url, data={'value': 'test'}).status_code == status.HTTP_403_FORBIDDEN
    assert api_client.patch(url, data={'value': 'test'}).status_code == status.HTTP_403_FORBIDDEN

    # can change for allowed questions
    choice: Choice = cast(Choice, question_1.choices.first())
    url = reverse('question-choices-detail', args=(choice.question.id, choice.id))
    response = api_client.put(url, data={'value': 'test'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['value'] == 'test'

    response = api_client.patch(url, data={'value': 'check'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['value'] == 'check'


#     user can add new choice
def test_user_can_add_choice_to_allowed_question_choice(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
) -> None:
    api_client.force_authenticate(user_1)
    assign_perm('questions.view_question', user_1)
    assign_perm('questions.change_question', user_1)
    question_1 = create_question('question_1')
    question_2 = create_question('question_2')

    assign_perm('questions.view_question', user_1, question_1)
    assign_perm('questions.change_question', user_1, question_1)

    # can't add new choicce for not allowed question
    url = reverse('question-choices-list', args=(question_2.id,))
    assert api_client.post(url, data={'value': 'test'}).status_code == status.HTTP_403_FORBIDDEN

    # can add new choice for allowed question
    url = reverse('question-choices-list', args=(question_1.id,))
    response = api_client.post(url, data={'value': 'test'})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['question'] == question_1.id


def test_user_can_delete_choice_from_allowed_question_choice(
    api_client: APIClient,
    user_1: ExampleUser,
    create_question: CreateQuestion,
) -> None:
    api_client.force_authenticate(user_1)
    assign_perm('questions.view_question', user_1)
    assign_perm('questions.change_question', user_1)
    question_1 = create_question('question_1')
    question_2 = create_question('question_2')

    assign_perm('questions.view_question', user_1, question_1)
    assign_perm('questions.change_question', user_1, question_1)

    # can't delete choicce from not allowed question
    choice_2: Choice = cast(Choice, question_2.choices.first())
    url = reverse('question-choices-detail', args=(choice_2.question.id, choice_2.id))
    assert (
        api_client.delete(
            url,
        ).status_code
        == status.HTTP_403_FORBIDDEN
    )

    # can add new choice for allowed question
    choice: Choice = cast(Choice, question_1.choices.first())
    url = reverse('question-choices-detail', args=(choice.question.id, choice.id))
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
