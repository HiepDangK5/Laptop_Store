from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app import models  # noqa: F401 - nạp model để SQLAlchemy tạo đủ bảng
from app.database import Base, engine

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Laptop Store")

# Tạo các bảng SQLite theo model khi ứng dụng khởi động.
Base.metadata.create_all(bind=engine)


@app.get("/", name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Trang chủ"},
    )
