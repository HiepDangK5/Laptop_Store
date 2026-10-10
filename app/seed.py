"""Thêm dữ liệu laptop mẫu vào SQLite: chạy bằng `python -m app.seed`."""

from app import models  # noqa: F401 - đăng ký model trước khi tạo bảng
from app.database import Base, SessionLocal, engine
from app.models import Laptop

# Giá tính bằng đồng; thông số dùng cho dữ liệu khởi tạo của cửa hàng.
LAPTOPS = [
    ("ASUS Vivobook Go 15 E1504FA", "ASUS", 10990000, "AMD Ryzen 5 7520U", 8, 512, "AMD Radeon 610M", False, 15.6, 1.63, 42, "văn phòng,học tập"),
    ("Acer Aspire Lite 14 AL14-31P", "Acer", 11990000, "Intel Core i3-N305", 8, 512, "Intel UHD Graphics", False, 14.0, 1.45, 58, "văn phòng,học tập"),
    ("Lenovo IdeaPad Slim 3 15AMN8", "Lenovo", 12990000, "AMD Ryzen 5 7520U", 16, 512, "AMD Radeon 610M", False, 15.6, 1.62, 47, "văn phòng,học tập"),
    ("HP Laptop 15-fc", "HP", 13990000, "AMD Ryzen 5 7530U", 16, 512, "AMD Radeon Graphics", False, 15.6, 1.59, 41, "văn phòng,học tập"),
    ("Dell Inspiron 15 3530", "Dell", 14990000, "Intel Core i5-1334U", 16, 512, "Intel Iris Xe Graphics", False, 15.6, 1.65, 54, "văn phòng,lập trình"),
    ("ASUS Vivobook 14 X1404VA", "ASUS", 15990000, "Intel Core i5-1335U", 16, 512, "Intel Iris Xe Graphics", False, 14.0, 1.40, 42, "văn phòng,học tập"),
    ("Acer Aspire 5 A515-58M", "Acer", 16990000, "Intel Core i5-13420H", 16, 512, "Intel UHD Graphics", False, 15.6, 1.77, 50, "văn phòng,lập trình"),
    ("Lenovo ThinkPad E14 Gen 6 AMD", "Lenovo", 17990000, "AMD Ryzen 5 7535U", 16, 512, "AMD Radeon 660M", False, 14.0, 1.44, 57, "văn phòng,lập trình"),
    ("MacBook Air 13 M2", "Apple", 19990000, "Apple M2 8-core", 8, 256, "Apple M2 8-core GPU", False, 13.6, 1.24, 52.6, "văn phòng,lập trình,đồ họa"),
    ("ASUS Vivobook S 14 OLED S5406", "ASUS", 21990000, "Intel Core Ultra 5 125H", 16, 512, "Intel Arc Graphics", False, 14.0, 1.30, 75, "văn phòng,lập trình,đồ họa"),
    ("HP ProBook 440 G11", "HP", 22990000, "Intel Core Ultra 5 125U", 16, 512, "Intel Graphics", False, 14.0, 1.39, 56, "văn phòng,lập trình"),
    ("Dell Inspiron 14 Plus 7440", "Dell", 23990000, "Intel Core Ultra 7 155H", 16, 512, "Intel Arc Graphics", False, 14.0, 1.60, 64, "lập trình,đồ họa"),
    ("Lenovo IdeaPad Pro 5 14AHP9", "Lenovo", 24990000, "AMD Ryzen 7 8845HS", 16, 512, "AMD Radeon 780M", False, 14.0, 1.46, 84, "lập trình,đồ họa"),
    ("Acer Aspire 5 A515-58GM RTX 2050", "Acer", 25990000, "Intel Core i5-13420H", 16, 512, "NVIDIA GeForce RTX 2050 4GB", True, 15.6, 1.80, 50, "lập trình,đồ họa,gaming"),
    ("ASUS TUF Gaming A15 FA507NU", "ASUS", 26990000, "AMD Ryzen 5 7535HS", 16, 512, "NVIDIA GeForce RTX 4050 6GB", True, 15.6, 2.20, 90, "gaming,đồ họa"),
    ("HP Victus 15-fa", "HP", 27990000, "Intel Core i5-13420H", 16, 512, "NVIDIA GeForce RTX 4050 6GB", True, 15.6, 2.29, 70, "gaming,đồ họa"),
    ("Lenovo LOQ 15IRX9", "Lenovo", 28990000, "Intel Core i5-13450HX", 16, 512, "NVIDIA GeForce RTX 4050 6GB", True, 15.6, 2.38, 60, "gaming,lập trình,đồ họa"),
    ("MSI Thin 15 B13VE", "MSI", 29990000, "Intel Core i7-13620H", 16, 512, "NVIDIA GeForce RTX 4050 6GB", True, 15.6, 1.86, 52.4, "gaming,lập trình,đồ họa"),
    ("ASUS Vivobook Pro 15 OLED K6502", "ASUS", 30990000, "Intel Core i7-13620H", 16, 512, "NVIDIA GeForce RTX 4050 6GB", True, 15.6, 1.80, 63, "đồ họa,lập trình,gaming"),
    ("Gigabyte G5 KF", "Gigabyte", 31990000, "Intel Core i7-13620H", 16, 512, "NVIDIA GeForce RTX 4060 8GB", True, 15.6, 2.08, 54, "gaming,đồ họa"),
    ("Acer Nitro V 15 ANV15-51", "Acer", 32990000, "Intel Core i7-13620H", 16, 512, "NVIDIA GeForce RTX 4060 8GB", True, 15.6, 2.10, 57.5, "gaming,đồ họa"),
    ("Lenovo Legion Slim 5 16APH8", "Lenovo", 34990000, "AMD Ryzen 7 7840HS", 16, 512, "NVIDIA GeForce RTX 4060 8GB", True, 16.0, 2.40, 80, "gaming,đồ họa,lập trình"),
    ("ASUS ROG Zephyrus G14 GA403", "ASUS", 36990000, "AMD Ryzen 9 8945HS", 16, 1000, "NVIDIA GeForce RTX 4060 8GB", True, 14.0, 1.50, 73, "gaming,đồ họa,lập trình"),
    ("Dell G15 5530 RTX 4060", "Dell", 37990000, "Intel Core i7-13650HX", 16, 1000, "NVIDIA GeForce RTX 4060 8GB", True, 15.6, 2.81, 86, "gaming,đồ họa,lập trình"),
    ("MSI Katana 15 B13VGK", "MSI", 39990000, "Intel Core i7-13620H", 16, 1000, "NVIDIA GeForce RTX 4070 8GB", True, 15.6, 2.25, 53.5, "gaming,đồ họa"),
]


def seed_laptops():
    # Chạy lại seed không tạo bản ghi trùng theo tên sản phẩm.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        existing_names = {name for (name,) in session.query(Laptop.name).all()}
        new_laptops = []
        for row in LAPTOPS:
            name, brand, price, cpu, ram, storage, gpu, dedicated, screen, weight, battery, tags = row
            if name in existing_names:
                continue
            new_laptops.append(
                Laptop(
                    name=name,
                    brand=brand,
                    price=price,
                    stock=5,
                    cpu=cpu,
                    ram_gb=ram,
                    storage_gb=storage,
                    gpu=gpu,
                    has_dedicated_gpu=dedicated,
                    screen_inch=screen,
                    weight_kg=weight,
                    battery_wh=battery,
                    use_tags=tags,
                    description=f"Laptop {brand} phù hợp với nhu cầu {tags}.",
                )
            )
        session.add_all(new_laptops)
        session.commit()
        print(f"Đã thêm {len(new_laptops)} laptop mới (danh sách seed có {len(LAPTOPS)} mẫu).")


if __name__ == "__main__":
    seed_laptops()
