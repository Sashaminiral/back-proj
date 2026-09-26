from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "workshop", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "workshop__title")
