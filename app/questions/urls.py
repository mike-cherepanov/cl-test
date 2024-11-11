from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import ChoicesViewSet, QuestionViewSet


router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='questions')
choices_router = NestedDefaultRouter(router, r'questions', lookup='question')
choices_router.register(r'choices', ChoicesViewSet, basename='question-choices')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(choices_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
