from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)


class Laptop(Base):
    __tablename__ = "laptops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    cpu = Column(String)
    ram_gb = Column(Integer)
    storage_gb = Column(Integer)
    gpu = Column(String)
    has_dedicated_gpu = Column(Boolean, nullable=False, default=False)
    screen_inch = Column(Float)
    weight_kg = Column(Float)
    battery_wh = Column(Float)
    use_tags = Column(Text)
    image_url = Column(String)
    description = Column(Text)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    total = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    laptop_id = Column(Integer, ForeignKey("laptops.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
