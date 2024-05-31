# Stdlib imports

# Core Django imports

from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

# Third-party app imports

# Imports from apps
from sam_store.users.api.views import UserViewSet
from shop.api.views import CategoryViewSet, ProductViewSet


router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register(r"users", UserViewSet,basename="users")
router.register(r"categories", CategoryViewSet, "categories")
router.register(r"product", ProductViewSet, "products")


app_name = "api"
urlpatterns = router.urls
