from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import POSSaleViewSet

router = DefaultRouter()
router.register(r'pos-transactions', POSSaleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]