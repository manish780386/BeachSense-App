from django.contrib import admin
from .models import Beach


@admin.register(Beach)
class BeachAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "district", "latitude", "longitude", "is_active", "updated_at")
    list_filter = ("state", "is_active")
    search_fields = ("name", "state", "district")
