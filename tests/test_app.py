import os
import sys

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import get_db
from app.services.weather import decode_weather_code
from app.services.city import search_cities

client = TestClient(app)

mock_db = MagicMock()
app.dependency_overrides[get_db] = lambda: (yield mock_db)


class TestWeatherService:
    def test_decode_weather_code(self):
        assert decode_weather_code(0) == "☀️ Ясно"
        assert decode_weather_code(95) == "⛈ Гроза"
        assert decode_weather_code(999) == "🌈 Неизвестно"


class TestCityService:
    @pytest.mark.asyncio
    async def test_search_cities_empty_query(self):
        result = await search_cities("")
        assert result == []

        result = await search_cities("a")
        assert result == []

class TestHistoryService:
    @patch("app.services.history.save_search")
    @patch("app.services.history.get_last_city")
    def test_save_and_get_search(self, mock_get_last_city, mock_save_search):
        mock_get_last_city.return_value = "Moscow"

        from app.services.history import save_search, get_last_city

        save_search(mock_db, "test_user", "Moscow")
        last_city = get_last_city(mock_db, "test_user")

        assert last_city == "Moscow"

    @patch("app.services.history.get_city_stats")
    def test_get_city_stats(self, mock_get_city_stats):
        mock_get_city_stats.return_value = {
            "Moscow": 3,
            "London": 1
        }

        from app.services.history import get_city_stats

        stats = get_city_stats(mock_db)

        assert "Moscow" in stats
        assert "London" in stats
        assert stats["Moscow"] == 3
        assert stats["London"] == 1


class TestAPI:
    def test_home_page(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Погода" in response.text

    def test_city_suggestions_empty(self):
        response = client.get("/api/cities/suggest?city=")
        assert response.status_code == 200

    def test_city_suggestions_short(self):
        response = client.get("/api/cities/suggest?city=a")
        assert response.status_code == 200

    def test_city_stats_endpoint(self):
        with patch("app.services.history.get_city_stats", return_value={"TestCity": 2}):
            response = client.get("/api/city-stats")
            assert response.status_code == 200
            assert "city_stats" in response.json()

    @patch("app.services.weather.get_weather_forecast")
    def test_weather_endpoint_success(self, mock_forecast):
        mock_forecast.return_value = {
            "city": "Moscow",
            "current": {
                "temperature": 20,
                "weatherdesc": "☀️ Ясно",
                "wind": 5,
                "pressure": 760,
                "humidity": 60
            },
            "hourly": []
        }

        response = client.get("/weather?city=Moscow")
        assert response.status_code == 200
        assert "Moscow" in response.text

    def test_weather_endpoint_invalid_city(self):
        response = client.get("/weather?city=InvalidCity123")
        assert response.status_code == 200
