"""Truy vấn laptop phù hợp với các bộ lọc tư vấn."""

from sqlalchemy import case, literal, or_

from app.database import SessionLocal
from app.models import Laptop


def _purpose_terms(purpose):
    """Đổi nhãn mục đích thành các từ khóa có trong use_tags."""
    if not isinstance(purpose, str) or not purpose.strip():
        return []

    text = purpose.strip().lower()
    if "đồ họa" in text or "đồ hoạ" in text or "video" in text:
        return ["đồ họa", "đồ hoạ"]
    if "văn phòng" in text:
        return ["văn phòng"]
    if "gaming" in text or "game" in text:
        return ["gaming"]
    if "lập trình" in text or "it" in text:
        return ["lập trình"]
    return [purpose.strip()]


def search_laptops(filters):
    """Tìm tối đa 5 laptop; trả về {"laptops": [...], "relaxed": bool}."""
    filters = filters if isinstance(filters, dict) else {}

    budget_min = filters.get("budget_min")
    budget_max = filters.get("budget_max")
    brand = filters.get("brand")
    purpose_terms = _purpose_terms(filters.get("purpose"))

    def run_query(min_price, max_price):
        with SessionLocal() as session:
            query = session.query(Laptop)
            conditions = []

            # Chỉ thêm điều kiện khi bộ lọc có giá trị.
            if min_price is not None:
                conditions.append(Laptop.price >= min_price)
            if max_price is not None:
                conditions.append(Laptop.price <= max_price)
            if filters.get("min_ram_gb") is not None:
                conditions.append(Laptop.ram_gb >= filters["min_ram_gb"])
            if filters.get("need_dedicated_gpu") is True:
                conditions.append(Laptop.has_dedicated_gpu.is_(True))
            if filters.get("max_weight_kg") is not None:
                conditions.append(Laptop.weight_kg <= filters["max_weight_kg"])
            if isinstance(brand, str) and brand.strip():
                conditions.append(Laptop.brand.ilike(f"%{brand.strip()}%"))
            if purpose_terms:
                conditions.append(
                    or_(*(Laptop.use_tags.ilike(f"%{term}%") for term in purpose_terms))
                )

            if conditions:
                # Các điều kiện được ghép bằng AND; riêng các từ khóa mục đích dùng OR.
                query = query.filter(*conditions)

            # Ưu tiên hãng trùng chính xác và mục đích phù hợp; sau đó giá thấp hơn.
            relevance = literal(0)
            if isinstance(brand, str) and brand.strip():
                relevance = relevance + case(
                    (Laptop.brand.ilike(brand.strip()), 2), else_=0
                )
            if purpose_terms:
                relevance = relevance + case(
                    (
                        or_(
                            *(Laptop.use_tags.ilike(f"%{term}%") for term in purpose_terms)
                        ),
                        1,
                    ),
                    else_=0,
                )

            return (
                query.order_by(
                    relevance.desc(), Laptop.price.asc(), Laptop.id.asc()
                )
                .limit(5)
                .all()
            )

    laptops = run_query(budget_min, budget_max)
    if laptops:
        return {"laptops": laptops, "relaxed": False}

    # Khi không có kết quả, nới cả cận dưới và cận trên ngân sách 15% nếu có.
    if budget_min is None and budget_max is None:
        return {"laptops": [], "relaxed": False}

    relaxed_min = round(budget_min * 0.85) if budget_min is not None else None
    relaxed_max = round(budget_max * 1.15) if budget_max is not None else None
    return {"laptops": run_query(relaxed_min, relaxed_max), "relaxed": True}
