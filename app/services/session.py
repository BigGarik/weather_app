from fastapi import Request, Response
from uuid import uuid4

# Простое хранилище сессий в памяти
sessions = {}

async def get_session_id(request: Request, response: Response) -> str:
    user_id = request.cookies.get("session_id")
    if not user_id:
        user_id = str(uuid4())
        response.set_cookie(key="session_id", value=user_id, httponly=True, max_age=86400)  # 24 часа
        sessions[user_id] = {}
    return user_id