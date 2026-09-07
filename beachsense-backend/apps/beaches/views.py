from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import viewsets, decorators, response, status

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
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = float(request.query_params.get("radius_km", 15))

        if not lat or not lng:
            return response.Response(
                {"detail": "lat and lng query params are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_location = Point(float(lng), float(lat), srid=4326)
        beaches = Beach.objects.filter(
            is_active=True,
            location__distance_lte=(user_location, D(km=radius_km)),
        )
        serializer = self.get_serializer(beaches, many=True)
        return response.Response(serializer.data)