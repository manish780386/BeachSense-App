from django.contrib.gis import admin
from .models import Beach


@admin.register(Beach)
class BeachAdmin(admin.GISModelAdmin):
    list_display = ("name", "state", "district", "is_active", "updated_at")
    list_filter = ("state", "is_active")
    search_fields = ("name", "state", "district")