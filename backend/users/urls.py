from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSetForRequests

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSetForRequests)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
