from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import PasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls', namespace='recipes')),
    path('api/', include('users.urls', namespace='users')),
    path(
        r'admin_password_reset/',
        PasswordResetView.as_view(),
        name='admin_password_reset'
    )
]
