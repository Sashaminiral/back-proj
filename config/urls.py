from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from bookings.views import BookingViewSet
from workshops.views import WorkshopViewSet

# REST-маршруты ViewSet'ов соответствуют стандартным CRUD-операциям.
router = DefaultRouter()
router.register("workshops", WorkshopViewSet, basename="workshop")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include(router.urls)),
]
