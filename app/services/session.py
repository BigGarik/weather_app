from fastapi import Request
from uuid import uuid4

def get_user_id(request: Request) -> str:
    """
    Получает user_id из cookies или создает новый.
    """
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid4())
    return user_id