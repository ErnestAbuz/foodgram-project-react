from api import views
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = 'api'

router_v1 = SimpleRouter()
router_v1.register('recipes', views.RecipeViewSet, basename='recipes')
router_v1.register('tags', views.TagViewSet, basename='tags')
router_v1.register(
    'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('users.urls')),
]
