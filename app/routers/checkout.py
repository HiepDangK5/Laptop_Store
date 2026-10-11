from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import get_current_user
from app.database import SessionLocal
from app.models import Laptop, Order, OrderItem, User
from app.routers.cart import read_cart

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


class CheckoutError(Exception):
    """Lỗi dữ liệu hoặc tồn kho trong quá trình đặt hàng."""


def load_cart_lines(cart: dict[str, int]):
    lines = []
    if not cart:
        return lines, 0

    laptop_ids = [int(laptop_id) for laptop_id in cart]
    with SessionLocal() as session:
        laptops = session.query(Laptop).filter(Laptop.id.in_(laptop_ids)).all()
        laptops_by_id = {laptop.id: laptop for laptop in laptops}
        for laptop_id, quantity in cart.items():
            laptop = laptops_by_id.get(int(laptop_id))
            if laptop is not None:
                lines.append(
                    {
                        "laptop": laptop,
                        "quantity": quantity,
                        "subtotal": laptop.price * quantity,
                    }
                )
    return lines, sum(line["subtotal"] for line in lines)


def render_checkout(request: Request, current_user: User, error: str | None = None, **values):
    lines, total = load_cart_lines(read_cart(request))
    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "title": "Thanh toán",
            "current_user": current_user,
            "cart_lines": lines,
            "total": total,
            "error": error,
            **values,
        },
    )


@router.post("/checkout/buy/{laptop_id}", name="buy_now")
def buy_now(request: Request, laptop_id: int):
    with SessionLocal() as session:
        if session.query(Laptop.id).filter(Laptop.id == laptop_id).first() is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    # Mua ngay chỉ checkout sản phẩm được chọn với số lượng một.
    request.session["cart"] = {str(laptop_id): 1}
    return RedirectResponse(url="/checkout", status_code=303)


@router.get("/checkout", name="checkout")
def checkout_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/login?next=%2Fcheckout", status_code=303)
    if not read_cart(request):
        return RedirectResponse(url="/cart", status_code=303)
    return render_checkout(request, current_user)


@router.post("/checkout", name="place_order")
async def place_order(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/login?next=%2Fcheckout", status_code=303)

    form = parse_qs((await request.body()).decode("utf-8"))
    receiver_name = form.get("receiver_name", [""])[0].strip()
    phone = form.get("phone", [""])[0].strip()
    address = form.get("address", [""])[0].strip()
    cart = read_cart(request)

    if not cart:
        return RedirectResponse(url="/cart", status_code=303)
    if not receiver_name or not phone or not address:
        return render_checkout(
            request,
            current_user,
            "Vui lòng nhập đầy đủ tên người nhận, số điện thoại và địa chỉ.",
            receiver_name=receiver_name,
            phone=phone,
            address=address,
        )

    try:
        # Tạo đơn, chốt giá hiện tại và trừ kho trong cùng transaction.
        with SessionLocal() as session:
            with session.begin():
                order = Order(
                    user_id=current_user.id,
                    receiver_name=receiver_name,
                    phone=phone,
                    address=address,
                    total=0,
                    status="Chờ xác nhận",
                )
                session.add(order)
                session.flush()

                total = 0
                for laptop_id, quantity in cart.items():
                    laptop_id_int = int(laptop_id)
                    laptop = session.query(Laptop).filter(Laptop.id == laptop_id_int).first()
                    if laptop is None:
                        raise CheckoutError("Một sản phẩm trong giỏ không còn tồn tại.")

                    # Cập nhật có điều kiện để không thể trừ kho nếu tồn kho đã thiếu.
                    updated_rows = (
                        session.query(Laptop)
                        .filter(Laptop.id == laptop_id_int, Laptop.stock >= quantity)
                        .update(
                            {Laptop.stock: Laptop.stock - quantity},
                            synchronize_session=False,
                        )
                    )
                    if updated_rows != 1:
                        raise CheckoutError(f"Sản phẩm {laptop.name} không đủ tồn kho.")

                    unit_price = laptop.price
                    total += unit_price * quantity
                    session.add(
                        OrderItem(
                            order_id=order.id,
                            laptop_id=laptop.id,
                            quantity=quantity,
                            unit_price=unit_price,
                        )
                    )

                order.total = total
                order_id = order.id
    except CheckoutError as error:
        return render_checkout(
            request,
            current_user,
            str(error),
            receiver_name=receiver_name,
            phone=phone,
            address=address,
        )

    request.session.pop("cart", None)
    return RedirectResponse(url=f"/checkout/success/{order_id}", status_code=303)


@router.get("/checkout/success/{order_id}", name="checkout_success")
def checkout_success(
    request: Request,
    order_id: int,
    current_user: User | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    with SessionLocal() as session:
        order = (
            session.query(Order)
            .filter(Order.id == order_id, Order.user_id == current_user.id)
            .first()
        )
        if order is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
        return templates.TemplateResponse(
            request=request,
            name="checkout_success.html",
            context={"title": "Đặt hàng thành công", "current_user": current_user, "order": order},
        )
