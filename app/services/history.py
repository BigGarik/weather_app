from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SearchHistory


def save_search(db: Session, user_id: str, city: str):
    """Сохранение поискового запроса."""
    db_search = SearchHistory(user_id=user_id, city=city)
    db.add(db_search)
    db.commit()


def get_last_city(db: Session, user_id: str) -> Optional[str]:
    """Получение последнего города, который искал пользователь."""
    last_search = db.query(SearchHistory).filter(SearchHistory.user_id == user_id).order_by(SearchHistory.timestamp.desc()).first()
    return last_search.city if last_search else None


def get_city_stats(db: Session) -> dict:
    """Получение статистики поисков по городам."""
    stats = db.query(SearchHistory.city, func.count(SearchHistory.city).label("count")).group_by(SearchHistory.city).all()
    return {city: count for city, count in stats}