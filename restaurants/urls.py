from django.urls import path, include
from rest_framework.routers import DefaultRouter

from restaurants.views import (
    DishModelViewSet,
    RestaurantModelViewSet,
    PrinterModelViewSet,
    OrderModelViewSet,
)


router = DefaultRouter()
router.register("dishes", DishModelViewSet)
router.register("restaurants", RestaurantModelViewSet)
router.register("printers", PrinterModelViewSet)
router.register("orders", OrderModelViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "restaurants"
