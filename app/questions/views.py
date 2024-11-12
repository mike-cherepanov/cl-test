from logging import getLogger
from typing import Any

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import ListView
from guardian.shortcuts import assign_perm
from rest_framework import permissions, viewsets
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from .models import Choice, Question
from .serializers import ChoiceSerializer, QuestionSerializer


logger = getLogger(__name__)


class QuestionPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        match request.method:
            case "OPTIONS":
                return True
            case "GET":
                return request.user.has_perm('questions.view_question')
            case "POST":
                return request.user.has_perm('questions.add_question')
            case "PUT":
                return request.user.has_perm('questions.change_question')
            case "PATCH":
                return request.user.has_perm('questions.change_question')
            case "DELETE":
                return request.user.has_perm('questions.delete_question')
        return False

    def has_object_permission(self, request: Request, view: APIView, obj: Question) -> bool:
        match request.method:
            case "OPTIONS":
                return True
            case "GET":
                return request.user.has_perm('questions.view_question', obj)
            case "POST":
                return request.user.has_perm('questions.add_question', obj)
            case "PUT":
                return request.user.has_perm('questions.change_question', obj)
            case "PATCH":
                return request.user.has_perm('questions.change_question', obj)
            case "DELETE":
                return request.user.has_perm('questions.delete_question', obj)
        return False


class QuestionChoicePermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return self.check_question_access(request, view)

    def has_object_permission(self, request: Request, view: APIView, obj: Choice) -> bool:
        return self.check_question_access(request, view)

    def check_question_access(self, request: Request, view: APIView) -> bool:
        try:
            question = Question.objects.get(id=view.kwargs.get('question_pk'))
        except Question.DoesNotExist:
            return False

        match request.method:
            case "OPTIONS":
                return True
            case "GET":
                return request.user.has_perm('questions.view_question', question)
            case "POST":
                return request.user.has_perm('questions.change_question', question)
            case "PUT":
                return request.user.has_perm('questions.change_question', question)
            case "PATCH":
                return request.user.has_perm('questions.change_question', question)
            case "DELETE":
                return request.user.has_perm('questions.change_question', question)
        return False


class QuestionViewSet(viewsets.ModelViewSet[Question]):
    queryset = Question.objects.none()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated & QuestionPermission]

    def perform_create(self, serializer: BaseSerializer[Question]) -> None:
        question = serializer.save()
        assign_perm('questions.view_question', self.request.user, question)
        assign_perm('questions.change_question', self.request.user, question)
        assign_perm('questions.delete_question', self.request.user, question)

    def get_queryset(self) -> QuerySet[Question]:
        match self.action:
            case "list":
                return Question.objects.with_permission(self.request.user, 'view_question')
            case _:
                return Question.objects.all()


class ChoicesViewSet(viewsets.ModelViewSet[Choice]):
    queryset = Choice.objects.none()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated & QuestionChoicePermission]

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        context['question'] = Question.objects.get(id=self.kwargs['question_pk'])
        return context

    def get_queryset(self) -> QuerySet[Choice]:
        if not self.request.user.is_authenticated:
            return Choice.objects.none()
        question = Question.objects.get(id=self.kwargs['question_pk'])
        match self.action:
            case "list":
                return Choice.objects.with_question_permission(self.request.user, 'view_question').filter(
                    question=question
                )
            case _:
                return Choice.objects.all()


class QuestionsListView(PermissionRequiredMixin, ListView):  # type: ignore
    model = Question
    template_name = 'question_list.html'
    permission_required = 'questions.view_question'

    def get_queryset(self) -> QuerySet[Question]:
        queryset = Question.objects.none()
        if page := self.kwargs.get('page'):
            if page == 'all':
                queryset = Question.objects.all()
            elif page == 'allowed':
                queryset = Question.objects.with_permission(self.request.user, 'questions.view_question')
        queryset = queryset.prefetch_related('choices')
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['page'] = self.kwargs.get('page')
        return context
