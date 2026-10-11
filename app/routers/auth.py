from pathlib import Path
from urllib.parse import parse_qs

import bcrypt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from app.auth import get_current_user
from app.database import SessionLocal
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def render_auth_page(request: Request, mode: str, error: str | None = None, **form_values):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={
            "title": "Đăng ký" if mode == "register" else "Đăng nhập",
            "mode": mode,
            "error": error,
            "current_user": get_current_user(request),
            **form_values,
        },
    )


async def read_form(request: Request) -> dict[str, str]:
    # Đọc form URL-encoded bằng thư viện chuẩn, không cần thêm package xử lý form.
    body = (await request.body()).decode("utf-8")
    return {key: values[0] for key, values in parse_qs(body).items() if values}


def set_user_session(request: Request, user_id: int):
    # Làm mới thông tin đăng nhập nhưng giữ giỏ khách đang có trong session.
    cart = request.session.get("cart")
    request.session.clear()
    if isinstance(cart, dict):
        request.session["cart"] = cart
    request.session["user_id"] = user_id


@router.get("/register", name="register")
def register_page(request: Request):
    return render_auth_page(request, "register")


@router.post("/register")
async def register(request: Request):
    form = await read_form(request)
    full_name = form.get("full_name", "").strip()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")

    if not full_name or "@" not in email or not password:
        return render_auth_page(
            request, "register", "Vui lòng nhập họ tên, email hợp lệ và mật khẩu.",
            full_name=full_name, email=email,
        )
    if len(password.encode("utf-8")) > 72:
        return render_auth_page(
            request, "register", "Mật khẩu không được dài quá 72 byte.",
            full_name=full_name, email=email,
        )

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with SessionLocal() as session:
        if session.query(User).filter(User.email == email).first():
            return render_auth_page(
                request, "register", "Email này đã được đăng ký.",
                full_name=full_name, email=email,
            )

        user = User(email=email, password_hash=password_hash, full_name=full_name)
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return render_auth_page(
                request, "register", "Email này đã được đăng ký.",
                full_name=full_name, email=email,
            )
        session.refresh(user)
        user_id = user.id

    # Tạo tài khoản xong thì đăng nhập luôn bằng user_id trong session.
    set_user_session(request, user_id)
    return RedirectResponse(url="/", status_code=303)


@router.get("/login", name="login")
def login_page(request: Request):
    return render_auth_page(
        request, "login", next_url=request.query_params.get("next", "/")
    )


@router.post("/login")
async def login(request: Request):
    form = await read_form(request)
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")

    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).first()
        valid_password = False
        if user and len(password.encode("utf-8")) <= 72:
            valid_password = bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))
        if not valid_password:
            return render_auth_page(
                request,
                "login",
                "Email hoặc mật khẩu không đúng.",
                email=email,
                next_url=form.get("next", "/"),
            )
        user_id = user.id

    set_user_session(request, user_id)
    next_url = form.get("next", "/")
    # Chỉ cho phép đường dẫn tương đối nội bộ để tránh redirect ra website khác.
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/"
    return RedirectResponse(url=next_url, status_code=303)


@router.post("/logout", name="logout")
def logout(request: Request):
    cart = request.session.get("cart")
    request.session.clear()
    if isinstance(cart, dict):
        request.session["cart"] = cart
    return RedirectResponse(url="/", status_code=303)
