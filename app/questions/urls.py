from django.shortcuts import redirect
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import ChoicesViewSet, QuestionsListView, QuestionViewSet


router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='questions')
choices_router = NestedDefaultRouter(router, r'questions', lookup='question')
choices_router.register(r'choices', ChoicesViewSet, basename='question-choices')

api_url_patters = [
    path('', include(router.urls)),
    path('', include(choices_router.urls)),
]

urlpatterns = [
    path('api/', include(api_url_patters)),
    path('', lambda *args, **kwargs: redirect('all-question-list', 'all')),
    path('questions/<str:page>', QuestionsListView.as_view(), name='all-question-list'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
