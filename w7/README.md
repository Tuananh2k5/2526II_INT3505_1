# Flask API & SQLite kết hợp OpenAPI

Đây là dự án API quản lý "Product" được xây dựng với `Flask`, `Flask-SQLAlchemy` (SQLite) và `connexion[swagger-ui]` dựa trên nguyên lý Service-Oriented Architecture (SOA).

## Cấu trúc thư mục

```text
/
├── app.py           # Entry point của ứng dụng
├── models.py        # Định nghĩa Cấu trúc cơ sở dữ liệu (ORM - SQLAlchemy)
├── handlers.py      # Xử lý các logic API (Controllers)
├── requirements.txt # File chứa tập tin các thư viện cần thiết
├── static/
│   └── openapi.yaml # File Schema API Specifications
└── README.md
```

## Hướng dẫn thiết lập môi trường

**Bước 1: Tạo môi trường ảo (venv)**
Mở Terminal/Powershell (trên thư mục dự án) và chạy lệnh:
```sh
# Trên Windows
python -m venv venv
```

**Bước 2: Kích hoạt môi trường ảo**
```sh
# Trên Windows
.\venv\Scripts\activate
```

**Bước 3: Cài đặt các thư viện cần thiết**
Tiến hành đưa các package yêu cầu vào môi trường hiện tại:
```sh
pip install -r requirements.txt
```

## Khởi động Server

Chạy lệnh để start API App (sẽ được host mặc định ở cổng 5000):
```sh
python app.py
```
*(Ghi chú: Lần chạy đầu tiên, SQLAlchemy sẽ tự tạo file `database.db`)*

## Truy cập giao diện Swagger UI

Sau khi server khởi động thành công, bạn có thể kiểm thử API trực quan dễ dàng (có UI tương tác đầy đủ tất cả phương thức CRUD đối với `Product`) tại:
[http://localhost:5000/api/ui/](http://localhost:5000/api/ui/)
