import httpx
from fastapi import HTTPException
from typing import Dict, Any

# Словарь: weathercode -> описание с эмодзи
WEATHER_CODE_MAP = {
    0: "☀️ Ясно",
    1: "🌤 Малооблачно",
    2: "⛅ Переменная облачность",
    3: "☁️ Пасмурно",
    45: "🌫 Туман",
    48: "🌫 Замерзающий туман",
    51: "🌦 Лёгкая морось",
    53: "🌧 Умеренная морось",
    55: "🌧 Сильная морось",
    61: "🌦 Лёгкий дождь",
    63: "🌧 Умеренный дождь",
    65: "🌧 Сильный дождь",
    71: "🌨 Лёгкий снег",
    73: "❄️ Умеренный снег",
    75: "❄️ Сильный снег",
    80: "🌦 Ливни",
    95: "⛈ Гроза",
    96: "⛈ Гроза с градом",
}

def decode_weather_code(code: int) -> str:
    return WEATHER_CODE_MAP.get(code, "🌈 Неизвестно")

async def get_city_coordinates(city: str) -> Dict[str, float]:
    """Получение координат города через Open-Meteo Geocoding API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1}
        )
        if response.status_code != 200 or not response.json().get("results"):
            raise HTTPException(status_code=404, detail="Город не найден")
        results = response.json()["results"][0]
        return {"latitude": results["latitude"], "longitude": results["longitude"]}

async def get_weather_forecast(city: str) -> Dict[str, Any]:
    coords = await get_city_coordinates(city)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "current": "temperature_2m,weathercode,windspeed_10m,pressure_msl,relative_humidity_2m",
                "hourly": "temperature_2m,weathercode",
                "forecast_days": 1
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при получении прогноза")
        data = response.json()
        return {
            "city": city,
            "current": {
                "temperature": data["current"]["temperature_2m"],
                "weathercode": data["current"]["weathercode"],
                "weatherdesc": decode_weather_code(data["current"]["weathercode"]),
                "wind": data["current"]["windspeed_10m"],
                "pressure": round(data["current"]["pressure_msl"] / 1.333),
                "humidity": data["current"]["relative_humidity_2m"]
            },
            "hourly": [
                {
                    "time": data["hourly"]["time"][i],
                    "temperature": data["hourly"]["temperature_2m"][i],
                    "weathercode": data["hourly"]["weathercode"][i],
                    "weatherdesc": decode_weather_code(data["hourly"]["weathercode"][i])
                }
                for i in range(0, 24, 3)
            ]
        }