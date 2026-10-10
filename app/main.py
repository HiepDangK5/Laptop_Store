from app import models  # noqa: F401 - nạp model để SQLAlchemy tạo đủ bảng
from app.database import Base, engine
from app.routers.products import router as products_router
from fastapi import FastAPI

app = FastAPI(title="Laptop Store")
app.include_router(products_router)

# Tạo các bảng SQLite theo model khi ứng dụng khởi động.
Base.metadata.create_all(bind=engine)
