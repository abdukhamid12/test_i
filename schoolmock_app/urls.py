from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'tests', TestViewSet)

urlpatterns = [
    path('home/', home, name="home"),
    path('test/', test, name="test-view"),
    path('', include('accounts.urls')),
]
