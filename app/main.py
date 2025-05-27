from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.city import search_cities
from app.services.history import save_search, get_last_city, get_city_stats
from app.services.session import get_session_id
from app.services.weather import get_weather_forecast

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request, response: Response, db: Session = Depends(get_db)):
    user_id = get_session_id(request, response)
    last_city = get_last_city(db, user_id)
    stats = get_city_stats(db)

    # Приветственное сообщение для возвращающихся пользователей
    welcome_message = None
    if last_city:
        welcome_message = f"С возвращением! Последний раз вы смотрели погоду в {last_city}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "last_city": last_city,
            "city_stats": stats,
            "welcome_message": welcome_message
        }
    )


@app.get("/weather")
async def weather(
        request: Request,
        city: str,
        response: Response,
        db: Session = Depends(get_db)
):
    user_id = get_session_id(request, response)

    try:
        forecast = await get_weather_forecast(city)
        save_search(db, user_id, city)
        stats = get_city_stats(db)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "forecast": forecast, "city": city, "last_city": city, "city_stats": stats}
        )
    except HTTPException as e:
        stats = get_city_stats(db)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": e.detail, "last_city": get_last_city(db, user_id), "city_stats": stats}
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
    stats = get_city_stats(db)
    return {"city_stats": stats}