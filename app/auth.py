from fastapi import Request

from app.database import SessionLocal
from app.models import User


def get_current_user(request: Request) -> User | None:
    """Lấy tài khoản từ user_id đã lưu trong session, dùng làm dependency chung."""
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None

    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            request.session.clear()
        return user
