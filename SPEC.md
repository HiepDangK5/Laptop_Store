# Web bán laptop có chatbot tư vấn AI
Vai trò: khách hàng, admin (cột users.is_admin).
Công nghệ: Python, FastAPI, SQLite + SQLAlchemy, Jinja2 + HTMX, Tailwind CDN,
bcrypt băm mật khẩu, session cookie (SessionMiddleware), python-dotenv.
LLM: [Gemini], chỉ gọi trong services/ai_service.py.
Cấu trúc: app/main.py, database.py, models.py, routers/, services/, templates/, static/
Bảng: users(id,email,password_hash,full_name,is_admin);
laptops(id,name,brand,price,stock,cpu,ram_gb,storage_gb,gpu,has_dedicated_gpu,
screen_inch,weight_kg,battery_wh,use_tags,image_url,description);
orders(id,user_id,receiver_name,phone,address,total,status,created_at);
order_items(id,order_id,laptop_id,quantity,unit_price).
Quy tắc: thông số lưu dạng số; giá khi thanh toán lấy từ DB; giỏ hàng lưu trong session;
thanh toán chỉ COD; thanh toán yêu cầu đăng nhập; không thêm tính năng ngoài danh sách này.