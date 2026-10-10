from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import distinct

from app.database import SessionLocal
from app.models import Laptop

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/", name="home")
def home(
    request: Request,
    brand: str | None = None,
    min_price: str = "",
    max_price: str = "",
):
    min_price = int(min_price) if min_price.strip() else None
    max_price = int(max_price) if max_price.strip() else None
    # Tạo truy vấn theo các bộ lọc được gửi qua query string.
    with SessionLocal() as session:
        brands = [row[0] for row in session.query(distinct(Laptop.brand)).order_by(Laptop.brand).all()]
        query = session.query(Laptop)

        if brand:
            query = query.filter(Laptop.brand == brand)
        if min_price is not None:
            query = query.filter(Laptop.price >= min_price)
        if max_price is not None:
            query = query.filter(Laptop.price <= max_price)

        laptops = query.order_by(Laptop.price, Laptop.id).all()
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "Laptop Store",
                "laptops": laptops,
                "brands": brands,
                "selected_brand": brand or "",
                "min_price": min_price,
                "max_price": max_price,
            },
        )


@router.get("/products/{laptop_id}", name="product_detail")
def product_detail(request: Request, laptop_id: int):
    with SessionLocal() as session:
        laptop = session.query(Laptop).filter(Laptop.id == laptop_id).first()
        if laptop is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

        return templates.TemplateResponse(
            request=request,
            name="product_detail.html",
            context={"title": laptop.name, "laptop": laptop},
        )