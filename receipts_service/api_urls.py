from django.urls import path, include


urlpatterns = [
    path("service/", include("restaurants.urls")),
    path("users/", include("users.urls")),
]
