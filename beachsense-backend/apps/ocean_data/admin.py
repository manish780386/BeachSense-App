from django.contrib import admin
from .models import OceanParameter


@admin.register(OceanParameter)
class OceanParameterAdmin(admin.ModelAdmin):
    list_display = (
        "beach", "wave_height_m", "wind_speed_kmph",
        "current_speed_kmph", "water_quality_index",
        "tsunami_alert", "storm_surge_alert", "recorded_at",
    )
    list_filter = ("tsunami_alert", "storm_surge_alert", "high_wave_alert")
    search_fields = ("beach__name",)