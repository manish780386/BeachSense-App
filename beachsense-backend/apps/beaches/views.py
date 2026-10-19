from rest_framework import viewsets, decorators, response, status

from .geo import beaches_within_radius
from .models import Beach
from .serializers import BeachSerializer, BeachDetailSerializer


class BeachViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/beaches/               -> list all beaches with latest status
    /api/beaches/{id}/          -> beach detail with raw ocean parameters
    /api/beaches/nearby/        -> ?lat=..&lng=..&radius_km=15
    """

    queryset = Beach.objects.filter(is_active=True)
    serializer_class = BeachSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BeachDetailSerializer
        return BeachSerializer

    @decorators.action(detail=False, methods=["get"])
    def nearby(self, request):
        try:
            lat = float(request.query_params.get("lat"))
            lng = float(request.query_params.get("lng"))
            radius_km = float(request.query_params.get("radius_km", 15))
        except (TypeError, ValueError):
            return response.Response(
                {"detail": "lat and lng query params are required and must be numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        beaches = beaches_within_radius(self.get_queryset(), lat, lng, radius_km)
        serializer = self.get_serializer(beaches, many=True)
        return response.Response(serializer.data)
