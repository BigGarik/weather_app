import pytest
import httpx
from unittest.mock import AsyncMock
from app.services.weather import get_city_coordinates, get_weather_forecast


@pytest.mark.asyncio
async def test_get_city_coordinates_success():
    # Мок для успешного ответа геокодирования
    mock_response = {
        "results": [{"latitude": 55.7558, "longitude": 37.6173}]
    }
    httpx.AsyncClient.get = AsyncMock(return_value=httpx.Response(200, json=mock_response))

    coords = await get_city_coordinates("Москва")
    assert coords == {"latitude": 55.7558, "longitude": 37.6173}


@pytest.mark.asyncio
async def test_get_city_coordinates_not_found():
    # Мок для случая, когда город не найден
    httpx.AsyncClient.get = AsyncMock(return_value=httpx.Response(200, json={}))

    with pytest.raises(httpx.HTTPStatusError) as exc:
        await get_city_coordinates("НеверныйГород")
    assert exc.value.response.status_code == 404


@pytest.mark.asyncio
async def test_get_weather_forecast():
    # Мок для геокодирования и прогноза
    mock_geo_response = {
        "results": [{"latitude": 55.7558, "longitude": 37.6173}]
    }
    mock_weather_response = {
        "current": {"temperature_2m": 15.0, "weathercode": 0},
        "hourly": {
            "time": ["2025-05-26T00:00", "2025-05-26T03:00"],
            "temperature_2m": [15.0, 14.5],
            "weathercode": [0, 1]
        }
    }
    httpx.AsyncClient.get = AsyncMock(side_effect=[
        httpx.Response(200, json=mock_geo_response),
        httpx.Response(200, json=mock_weather_response)
    ])

    forecast = await get_weather_forecast("Москва")
    assert forecast["city"] == "Москва"
    assert forecast["current"]["temperature"] == 15.0
    assert len(forecast["hourly"]) == 2