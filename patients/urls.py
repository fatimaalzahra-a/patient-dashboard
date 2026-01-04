from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ERVisitViewSet, CommunicationEventViewSet,
    SatisfactionSignalViewSet, ExperienceFailureIndicatorViewSet
)

router = DefaultRouter()
router.register(r'visits', ERVisitViewSet)
router.register(r'communication-events', CommunicationEventViewSet)
router.register(r'feedback', SatisfactionSignalViewSet)
router.register(r'failure-indicators', ExperienceFailureIndicatorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]