from uuid import uuid4

from fastapi import Request, Response


def get_session_id(request: Request, response: Response) -> str:
    """
    Получает или создает session_id для пользователя.
    Сохраняет его в cookies на 30 дней.
    """
    user_id = request.cookies.get("session_id")

    if not user_id:
        user_id = str(uuid4())
        # Устанавливаем cookie на 30 дней
        response.set_cookie(
            key="session_id",
            value=user_id,
            httponly=True,
            max_age=30 * 24 * 60 * 60,  # 30 дней в секундах
            samesite="lax"
        )

    return user_id