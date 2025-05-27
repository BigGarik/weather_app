import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Убеждаемся что директория для БД существует
os.makedirs("app/data", exist_ok=True)

DATABASE_URL = "sqlite:///app/data/history.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    city = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Создаем таблицы
Base.metadata.create_all(bind=engine)


def get_db():
    """Генератор подключения к БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()