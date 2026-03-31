# Bài tập Buổi 5: Data Modeling và Resource Design

Dự án này thực hiện các yêu cầu thực hành dựa trên API quản lý thư viện (Library Management System). API được thiết kế bằng FastAPI.

## Yêu cầu đã hiện thực hóa
Theo đúng mô tả trong bài giảng của buổi 5, server tích hợp các kĩ thuật sau:

- **Thiết kế data model:** Xây dựng cấu trúc cho lĩnh vực quản lý thư viện với 3 model chính là `Book` (sách), `User` (người dùng) và `BorrowRecord` (hồ sơ mượn). 
- **Thiết kế resource tree phù hợp với domain:** Thực hành cách tổ chức URL resource lồng nhau (nested resource) với 2 REST endpoints mẫu:
  - `GET /users/{user_id}/borrows`: Xem sách mà user cụ thể đã mượn
  - `POST /users/{user_id}/borrows`: Ghi nhận thêm lần mượn sách mới cho user  
- **Thiết kế endpoint tìm kiếm:** Tìm kiếm qua query params `GET /books/search?q=từ_khóa`.
- **Thực hành các chiến lược phân trang (Pagination):**
  - **Offset/Limit:** `GET /books/offset?offset=0&limit=10`
  - **Page-based:** `GET /books/page?page=1&size=10`  
  - **Cursor-based:** `GET /books/cursor?cursor=10&limit=10`

---

## Hướng dẫn cài đặt và chạy server

**Yêu cầu:** Đã cài đặt Python 3.7 trở lên trên máy tính của bạn.

### Bước 1: Cài đặt thư viện
Bạn hãy mở terminal/command prompt tại thư mục này (`w5`) và chạy lệnh sau để tải các package:
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy server
Sử dụng công cụ `uvicorn` (được cài mặc định trong tệp yêu cầu rỗng) để chạy:
```bash
uvicorn main:app --reload
```

### Bước 3: Kiểm tra thử API (Auto Swagger UI)
Tính năng rất tiện lợi của FastAPI là trang tài liệu sẽ tự sinh. Vì vậy bạn hãy truy cập đường dẫn sau trên trình duyệt để kiểm tra:
* **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Tại trang này, bạn có thể thực hiện thao tác **"Try it out"** trên tất cả endpoint để chạy thử các phương thức tìm kiếm, lấy dữ liệu và theo dõi phân trang trả về một cách trực quan.
