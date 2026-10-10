import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# SQLite lưu dữ liệu vào file cục bộ trong thư mục chạy ứng dụng.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./laptop_store.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
