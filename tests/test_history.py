import pytest
from sqlalchemy.orm import Session
from app.database import SearchHistory, get_db
from app.services.history import save_search, get_last_city, get_city_stats

@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    SearchHistory.metadata.create_all(engine)
    db = SessionLocal()
    yield db
    db.close()

@pytest.mark.asyncio
async def test_save_search(db_session: Session):
    save_search(db_session, "user1", "Москва")
    search = db_session.query(SearchHistory).filter_by(user_id="user1", city="Москва").first()
    assert search is not None
    assert search.city == "Москва"

@pytest.mark.asyncio
async def test_get_last_city(db_session: Session):
    save_search(db_session, "user1", "Москва")
    save_search(db_session, "user1", "Казань")
    last_city = get_last_city(db_session, "user1")
    assert last_city == "Казань"

@pytest.mark.asyncio
async def test_get_city_stats(db_session: Session):
    save_search(db_session, "user1", "Москва")
    save_search(db_session, "user2", "Москва")
    save_search(db_session, "user1", "Казань")
    stats = get_city_stats(db_session)
    assert stats == {"Москва": 2, "Казань": 1}