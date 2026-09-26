from django.contrib import admin

from workshops.models import Workshop


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "capacity", "location", "created_by")
    search_fields = ("title", "location")
    list_filter = ("starts_at",)
