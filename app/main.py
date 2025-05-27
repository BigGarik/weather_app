from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.city import search_cities
from app.services.history import save_search, get_last_city, get_city_stats
from app.services.session import get_user_id
from app.services.weather import get_weather_forecast

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """Middleware для автоматического управления сессиями."""
    response = await call_next(request)

    # Устанавливаем cookie если его нет
    if "user_id" not in request.cookies:
        user_id = get_user_id(request)
        response.set_cookie(
            key="user_id",
            value=user_id,
            httponly=True,
            max_age=30 * 24 * 60 * 60,  # 30 дней
            samesite="lax"
        )

    return response


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Главная страница."""
    user_id = get_user_id(request)
    last_city = get_last_city(db, user_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "last_city": last_city
        }
    )


@app.get("/weather")
async def weather(
        request: Request,
        city: str,
        db: Session = Depends(get_db)
):
    """Запрос погоды."""
    user_id = get_user_id(request)

    try:
        forecast = await get_weather_forecast(city)
        save_search(db, user_id, city)

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "forecast": forecast, "city": city, "last_city": city}
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": e.detail, "last_city": get_last_city(db, user_id)}
        )


@app.get("/api/cities/suggest")
async def suggest_cities(request: Request, city: Optional[str] = Query(None)):
    """Автодополнение городов через API."""
    if not city or len(city.strip()) < 2:
        suggestions = []
    else:
        suggestions = await search_cities(city.strip())

    return templates.TemplateResponse(
        "suggestions.html",
        {"request": request, "suggestions": suggestions}
    )


@app.get("/api/city-stats")
async def city_stats(db: Session = Depends(get_db)):
    """Статистика поиска."""
    stats = get_city_stats(db)
    return {"city_stats": stats}