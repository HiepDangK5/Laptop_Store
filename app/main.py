import os
from pathlib import Path

from app import models  # noqa: F401 - nạp model để SQLAlchemy tạo đủ bảng
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(title="Laptop Store")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "development-secret-change-before-deploy"),
    same_site="lax",
    https_only=False,
)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(products_router)
app.include_router(auth_router)

# Tạo các bảng SQLite theo model khi ứng dụng khởi động.
Base.metadata.create_all(bind=engine)
