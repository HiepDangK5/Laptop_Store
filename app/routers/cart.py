from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import get_current_user
from app.database import SessionLocal
from app.models import Laptop, User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def read_cart(request: Request) -> dict[str, int]:
    """Chuẩn hóa giỏ từ session; chỉ giữ ID sản phẩm và số lượng."""
    stored_cart = request.session.get("cart", {})
    if not isinstance(stored_cart, dict):
        return {}

    cart = {}
    for laptop_id, quantity in stored_cart.items():
        try:
            laptop_id = str(int(laptop_id))
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        if int(laptop_id) > 0 and quantity > 0:
            cart[laptop_id] = quantity
    return cart


@router.get("/cart", name="cart")
def view_cart(request: Request, current_user: User | None = Depends(get_current_user)):
    cart = read_cart(request)
    cart_lines = []

    if cart:
        laptop_ids = [int(laptop_id) for laptop_id in cart]
        with SessionLocal() as session:
            laptops = session.query(Laptop).filter(Laptop.id.in_(laptop_ids)).all()
            laptops_by_id = {laptop.id: laptop for laptop in laptops}

            # Tên và giá luôn đọc mới từ DB, không lấy từ session.
            for laptop_id, quantity in cart.items():
                laptop = laptops_by_id.get(int(laptop_id))
                if laptop is None:
                    continue
                cart_lines.append(
                    {
                        "laptop": laptop,
                        "quantity": quantity,
                        "subtotal": laptop.price * quantity,
                    }
                )

    total = sum(line["subtotal"] for line in cart_lines)
    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "title": "Giỏ hàng",
            "current_user": current_user,
            "cart_lines": cart_lines,
            "total": total,
        },
    )


@router.post("/cart/add/{laptop_id}", name="cart_add")
def add_to_cart(request: Request, laptop_id: int):
    with SessionLocal() as session:
        if session.query(Laptop.id).filter(Laptop.id == laptop_id).first() is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    cart = read_cart(request)
    key = str(laptop_id)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)


@router.post("/cart/update/{laptop_id}", name="cart_update")
async def update_cart(request: Request, laptop_id: int):
    form = parse_qs((await request.body()).decode("utf-8"))
    try:
        quantity = int(form.get("quantity", ["1"])[0])
    except ValueError:
        quantity = 0

    cart = read_cart(request)
    key = str(laptop_id)
    if key in cart and quantity > 0:
        cart[key] = quantity
    request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)


@router.post("/cart/remove/{laptop_id}", name="cart_remove")
def remove_from_cart(request: Request, laptop_id: int):
    cart = read_cart(request)
    cart.pop(str(laptop_id), None)
    request.session["cart"] = cart
    return RedirectResponse(url="/cart", status_code=303)
