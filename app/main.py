from pathlib import Path

from app import models  # noqa: F401 - nạp model để SQLAlchemy tạo đủ bảng
from app.database import Base, engine
from app.routers.products import router as products_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Laptop Store")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(products_router)

# Tạo các bảng SQLite theo model khi ứng dụng khởi động.
Base.metadata.create_all(bind=engine)
