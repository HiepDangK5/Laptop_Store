from pathlib import Path
from time import time
from urllib.parse import parse_qs, quote

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.ai_service import extract_filters, generate_advice
from app.services.product_service import search_laptops

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
IMAGE_DIR = Path(__file__).resolve().parent.parent / "static" / "images"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
FALLBACK_ANSWER = (
    "Hiện trợ lý chưa kết nối được Gemini. Bạn có thể thử gửi lại sau hoặc xem "
    "các sản phẩm trên trang."
)


def _product_image_url(laptop):
    # Dùng ảnh đã lưu; nếu chưa có thì tìm ảnh cùng tên trong static/images.
    if laptop.image_url:
        return laptop.image_url
    for image_path in IMAGE_DIR.glob(f"{laptop.name}.*"):
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_SUFFIXES:
            return f"/static/images/{quote(image_path.name)}"
    return None


def _render_messages(request, history, laptops=None, error=None):
    laptops = laptops or []
    return templates.TemplateResponse(
        request=request,
        name="partials/chat_messages.html",
        context={
            "history": history,
            "laptops": laptops,
            "image_urls": {laptop.id: _product_image_url(laptop) for laptop in laptops},
            "chat_error": error,
        },
    )


@router.post("/chat", name="chat")
async def chat(request: Request):
    # HTMX gửi form URL-encoded; phân tích trực tiếp để không cần thêm thư viện.
    form = parse_qs((await request.body()).decode("utf-8"))
    question = form.get("question", [""])[0].strip()
    history = request.session.get("chat_history", [])
    if not isinstance(history, list):
        history = []

    if not question:
        return _render_messages(request, history, error="Hãy nhập câu hỏi trước khi gửi.")
    if len(question) > 500:
        return _render_messages(request, history, error="Câu hỏi tối đa 500 ký tự.")

    # Giữ các mốc thời gian trong 60 giây để giới hạn 10 câu hỏi mỗi session.
    now = time()
    recent_requests = request.session.get("chat_request_times", [])
    if not isinstance(recent_requests, list):
        recent_requests = []
    recent_requests = [stamp for stamp in recent_requests if isinstance(stamp, (int, float)) and now - stamp < 60]
    if len(recent_requests) >= 10:
        return _render_messages(
            request,
            history,
            error="Bạn đã gửi 10 tin nhắn trong một phút. Vui lòng chờ một chút rồi thử lại.",
        )
    recent_requests.append(now)
    request.session["chat_request_times"] = recent_requests

    laptops = []
    try:
        filters = extract_filters(question, history)
    except (RuntimeError, TimeoutError, OSError):
        # Bao gồm thiếu API key, Gemini báo lỗi hoặc hết thời gian chờ.
        answer = FALLBACK_ANSWER
    else:
        if filters.get("need_clarify"):
            answer = filters.get("clarify_question") or "Bạn cho biết thêm ngân sách và mục đích sử dụng laptop nhé."
        else:
            result = search_laptops(filters)
            laptops = result["laptops"]
            try:
                answer = generate_advice(question, laptops, result["relaxed"])
            except (RuntimeError, TimeoutError, OSError):
                answer = FALLBACK_ANSWER

    # Lưu câu hỏi và câu trả lời; cookie session chỉ giữ sáu tin nhắn gần nhất.
    history.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    )
    history = history[-6:]
    request.session["chat_history"] = history
    return _render_messages(request, history, laptops=laptops)
