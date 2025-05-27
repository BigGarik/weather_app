from unittest.mock import patch

import httpx
import pytest

from app.services.city import search_cities


@pytest.mark.asyncio
async def test_search_cities_success():
    """Тест успешного поиска городов."""
    mock_response = {
        "results": [
            {"name": "Москва", "country": "Россия"},
            {"name": "Мюнхен", "country": "Германия"}
        ]
    }

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_response)

        results = await search_cities("Мос")
        assert len(results) == 2
        assert results[0]["name"] == "Москва"
        assert results[0]["country"] == "Россия"


@pytest.mark.asyncio
async def test_search_cities_empty_query():
    """Тест с пустым запросом."""
    results = await search_cities("")
    assert results == []

    results = await search_cities("М")  # Меньше 2 символов
    assert results == []


@pytest.mark.asyncio
async def test_search_cities_api_error():
    """Тест обработки ошибки API."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = Exception("API Error")

        results = await search_cities("Москва")
        assert results == []


@pytest.mark.asyncio
async def test_search_cities_no_results():
    """Тест когда API не возвращает результатов."""
    mock_response = {"results": []}

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = httpx.Response(200, json=mock_response)

        results = await search_cities("НесуществующийГород")
        assert results == []