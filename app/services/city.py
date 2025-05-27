import httpx
from typing import List, Dict


async def search_cities(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """
    Поиск городов через Open-Meteo Geocoding API.
    Возвращает список городов с названием и страной.
    """
    if len(query.strip()) < 2:
        return []

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": query,
                    "count": limit,
                    "language": "ru"
                }
            )

            if response.status_code != 200:
                return []

            data = response.json()
            cities = []

            for result in data.get("results", []):
                city_name = result.get("name", "")
                country = result.get("country", "")

                if city_name:
                    cities.append({
                        "name": city_name,
                        "country": country or "Неизвестно"
                    })

            return cities

    except Exception:
        # В случае ошибки возвращаем пустой список
        return []