from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.services.weather import get_weather_forecast
from app.services.history import save_search, get_last_city, get_city_stats
from app.services.session import get_session_id
from app.database import get_db
from sqlalchemy.orm import Session

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db), user_id: str = Depends(get_session_id)):
    last_city = get_last_city(db, user_id)
    stats = get_city_stats(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "last_city": last_city, "city_stats": stats}
    )

@app.get("/weather")
async def weather(
    request: Request,
    city: str,
    response: Response,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_session_id)
):
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


@app.get("/api/city-stats")
async def city_stats(db: Session = Depends(get_db)):
    stats = get_city_stats(db)
    return {"city_stats": stats}