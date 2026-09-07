from rest_framework import serializers
from .models import Beach
from apps.suitability.models import SuitabilityStatus


class BeachSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Beach
        fields = [
            "id", "name", "state", "district",
            "latitude", "longitude", "current_status", "is_active",
        ]

    def get_latitude(self, obj):
        return obj.location.y

    def get_longitude(self, obj):
        return obj.location.x

    def get_current_status(self, obj):
        latest = (
            SuitabilityStatus.objects.filter(beach=obj)
            .order_by("-computed_at")
            .first()
        )
        if not latest:
            return None
        return {
            "status": latest.status,
            "score": latest.score,
            "computed_at": latest.computed_at,
        }


class BeachDetailSerializer(BeachSerializer):
    """Extended serializer used for the single-beach detail endpoint,
    includes the latest raw ocean parameters alongside the status."""

    parameters = serializers.SerializerMethodField()

    class Meta(BeachSerializer.Meta):
        fields = BeachSerializer.Meta.fields + ["parameters"]

    def get_parameters(self, obj):
        from apps.ocean_data.models import OceanParameter
        latest = (
            OceanParameter.objects.filter(beach=obj)
            .order_by("-recorded_at")
            .first()
        )
        if not latest:
            return None
        return {
            "wave_height_m": latest.wave_height_m,
            "wind_speed_kmph": latest.wind_speed_kmph,
            "current_speed_kmph": latest.current_speed_kmph,
            "water_quality_index": latest.water_quality_index,
            "tsunami_alert": latest.tsunami_alert,
            "storm_surge_alert": latest.storm_surge_alert,
            "high_wave_alert": latest.high_wave_alert,
            "recorded_at": latest.recorded_at,
        }