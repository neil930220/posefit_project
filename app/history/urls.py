from rest_framework.routers import DefaultRouter
from .views import FoodEntryViewSet

router = DefaultRouter()
router.register(r"entries", FoodEntryViewSet, basename="foodentry")

urlpatterns = router.urls
