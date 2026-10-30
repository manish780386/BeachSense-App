"""
Automated tests for BeachSense.

Run with:   python manage.py test

Covers: the suitability scoring engine, the full data pipeline
(ocean data -> suitability status) and the REST API endpoints.
"""

from unittest.mock import patch

from django.test import TestCase

from apps.beaches.models import Beach
from apps.ocean_data.models import OceanParameter
from apps.ocean_data.tasks import fetch_incois_data
from apps.suitability.engine import calculate_suitability
from apps.suitability.models import SuitabilityStatus
from apps.suitability.tasks import compute_all_suitability


def reading(wave=0.0, wind=0.0, current=0.0, quality=100.0, tsunami=False, surge=False):
    return {
        "wave_height_m": wave, "wind_speed_kmph": wind, "current_speed_kmph": current,
        "water_quality_index": quality, "tsunami_alert": tsunami, "storm_surge_alert": surge,
        "high_wave_alert": wave > 2.5,
    }


class ScoringEngineTests(TestCase):
    def test_calm_sea_is_suitable(self):
        status, score, _ = calculate_suitability(reading(0.5, 10, 1, 90))
        self.assertEqual(status, "SUITABLE")
        self.assertGreaterEqual(score, 70)

    def test_worked_example_from_presentation(self):
        # 100 - 27 (wave 1.8) - 15 (wind 30) - 6 (current 3) = 52
        status, score, _ = calculate_suitability(reading(1.8, 30, 3, 100))
        self.assertEqual((status, score), ("CAUTION", 52.0))

    def test_rough_sea_is_not_suitable(self):
        status, score, _ = calculate_suitability(reading(3.2, 50, 10, 55))
        self.assertEqual(status, "NOT_SUITABLE")
        self.assertLess(score, 40)

    def test_tsunami_alert_overrides_calm_conditions(self):
        status, score, reason = calculate_suitability(reading(0.2, 5, 0.5, 100, tsunami=True))
        self.assertEqual((status, score), ("NOT_SUITABLE", 0.0))
        self.assertIn("Tsunami", reason)

    def test_storm_surge_alert_overrides_calm_conditions(self):
        status, score, reason = calculate_suitability(reading(0.2, 5, 0.5, 100, surge=True))
        self.assertEqual((status, score), ("NOT_SUITABLE", 0.0))
        self.assertIn("Storm surge", reason)

    def test_boundary_score_70_is_suitable(self):
        status, score, _ = calculate_suitability(reading(wave=2.0))  # 100 - 30
        self.assertEqual((status, score), ("SUITABLE", 70.0))

    def test_boundary_score_40_is_caution(self):
        status, score, _ = calculate_suitability(reading(4, 20, 5, 100))  # 100 - 40 - 10 - 10
        self.assertEqual((status, score), ("CAUTION", 40.0))

    def test_just_below_40_is_not_suitable(self):
        status, _, _ = calculate_suitability(reading(4, 20, 5, 99))
        self.assertEqual(status, "NOT_SUITABLE")

    def test_each_parameter_deduction_is_capped(self):
        # absurd wave height cannot push the score below 100 - 40 on its own
        _, score, _ = calculate_suitability(reading(wave=50))
        self.assertEqual(score, 60.0)

    def test_score_never_negative(self):
        _, score, _ = calculate_suitability(reading(9, 200, 50, 0))
        self.assertGreaterEqual(score, 0)

    def test_poor_water_quality_lowers_score(self):
        _, good, _ = calculate_suitability(reading(1, 10, 1, 100))
        _, poor, _ = calculate_suitability(reading(1, 10, 1, 20))
        self.assertGreater(good, poor)


class DataPipelineTests(TestCase):
    def setUp(self):
        self.beach = Beach.objects.create(name="Test Beach", state="Goa", latitude=15.5, longitude=73.7)

    def test_fetch_task_stores_one_reading_per_active_beach(self):
        with patch("apps.ocean_data.tasks.fetch_reading_for_beach", return_value={
            "wave_height_m": 1.0, "wind_speed_kmph": 12.0, "current_speed_kmph": 1.0,
            "water_quality_index": 90.0, "tsunami_alert": False, "storm_surge_alert": False,
            "high_wave_alert": False, "source": "TEST",
        }):
            fetch_incois_data()
        self.assertEqual(OceanParameter.objects.filter(beach=self.beach).count(), 1)

    def test_compute_task_uses_latest_reading_and_stores_status(self):
        OceanParameter.objects.create(beach=self.beach, wave_height_m=0.4, wind_speed_kmph=8,
                                      current_speed_kmph=1, water_quality_index=95)
        compute_all_suitability()
        status = SuitabilityStatus.objects.get(beach=self.beach)
        self.assertEqual(status.status, "SUITABLE")

    def test_inactive_beaches_are_skipped(self):
        self.beach.is_active = False
        self.beach.save()
        OceanParameter.objects.create(beach=self.beach, wave_height_m=1, wind_speed_kmph=1, current_speed_kmph=1)
        compute_all_suitability()
        self.assertFalse(SuitabilityStatus.objects.exists())


class ApiTests(TestCase):
    def setUp(self):
        self.baga = Beach.objects.create(name="Baga Beach", state="Goa", latitude=15.5553, longitude=73.7517)
        self.calangute = Beach.objects.create(name="Calangute Beach", state="Goa", latitude=15.5439, longitude=73.7553)
        self.marina = Beach.objects.create(name="Marina Beach", state="Tamil Nadu", latitude=13.05, longitude=80.2824)
        OceanParameter.objects.create(beach=self.baga, wave_height_m=0.5, wind_speed_kmph=10, current_speed_kmph=1)
        SuitabilityStatus.objects.create(beach=self.baga, status="SUITABLE", score=88.0, reason="ok")

    def test_list_returns_all_beaches_with_status(self):
        r = self.client.get("/api/beaches/")
        self.assertEqual(r.status_code, 200)
        by_name = {b["name"]: b for b in r.json()}
        self.assertEqual(len(by_name), 3)
        self.assertEqual(by_name["Baga Beach"]["current_status"]["status"], "SUITABLE")
        self.assertIsNone(by_name["Marina Beach"]["current_status"])  # no data yet -> null, not an error

    def test_detail_includes_live_parameters(self):
        data = self.client.get(f"/api/beaches/{self.baga.id}/").json()
        self.assertEqual(data["parameters"]["wave_height_m"], 0.5)

    def test_nearby_returns_only_beaches_in_radius_nearest_first(self):
        data = self.client.get("/api/beaches/nearby/?lat=15.55&lng=73.75&radius_km=15").json()
        names = [b["name"] for b in data]
        self.assertEqual(names, ["Baga Beach", "Calangute Beach"])
        self.assertLessEqual(data[0]["distance_km"], data[1]["distance_km"])

    def test_nearby_without_coordinates_is_rejected(self):
        self.assertEqual(self.client.get("/api/beaches/nearby/").status_code, 400)

    def test_unknown_beach_is_404(self):
        self.assertEqual(self.client.get("/api/beaches/9999/").status_code, 404)

    def test_swagger_docs_are_served(self):
        self.assertEqual(self.client.get("/api/docs/").status_code, 200)
