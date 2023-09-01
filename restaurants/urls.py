from django.urls import path, include
from rest_framework.routers import DefaultRouter

from restaurants.views import (
    DishModelViewSet,
    RestaurantModelViewSet,
    PrinterModelViewSet,
    OrderModelViewSet,
)


router = DefaultRouter()
router.register(r"dishes", DishModelViewSet)
router.register(r"restaurants", RestaurantModelViewSet)
router.register(r"printers", PrinterModelViewSet)
router.register(r"orders", OrderModelViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "restaurants"
