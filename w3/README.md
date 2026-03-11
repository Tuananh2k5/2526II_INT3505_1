# REST API Demo - Week 3

Server Flask minh họa cách thiết kế REST API theo các nguyên tắc:

- Nhất quán (**consistency**)
- Dễ hiểu (**clarity**)
- Dễ mở rộng (**extensibility**)

Resource chính: `books` (danh từ số nhiều, lowercase, có versioning `/api/v1`).

---

## 1. Chuẩn bị môi trường

- Python 3.x đã cài đặt sẵn.
- Thư viện `Flask`:

```bash
pip install flask
```

Nên chạy lệnh này trong virtualenv nếu đây là project lớn.

---

## 2. Cấu trúc file chính

Trong thư mục `w3`:

- `rest_api_server.py`: code Flask server.
- `postman_collection.json`: collection để import vào Postman.
- `README.md`: file hướng dẫn này.

---

## 3. Cách chạy server

Mở terminal tại thư mục gốc project và chạy:

```bash
python w3/rest_api_server.py
```

Nếu dùng PowerShell, cũng tương tự:

```powershell
python w3/rest_api_server.py
```

Server sẽ chạy ở địa chỉ:

- Base URL: `http://localhost:5004`
- Base path API: `/api/v1`

Ví dụ endpoint đầy đủ: `http://localhost:5004/api/v1/books`

---

## 4. Danh sách endpoint

- `GET /api/v1/health-check`
  - Kiểm tra server đang chạy.

- `GET /api/v1/books`
  - Lấy danh sách tất cả books.
  - Query params hỗ trợ:
    - `author`: lọc theo tên tác giả (exact match).

- `POST /api/v1/books`
  - Tạo mới một book.
  - Body JSON ví dụ:

    ```json
    {
      "title": "Clean Code",
      "author": "Robert C. Martin"
    }
    ```

- `GET /api/v1/books/<book_id>`
  - Lấy chi tiết 1 book theo id.

- `PUT /api/v1/books/<book_id>`
  - Cập nhật toàn bộ thông tin 1 book.
  - Body JSON yêu cầu đầy đủ `title` và `author`:

    ```json
    {
      "title": "New Title",
      "author": "New Author"
    }
    ```

- `DELETE /api/v1/books/<book_id>`
  - Xóa 1 book theo id.

---

## 5. Test chi tiết bằng Postman

### 5.1. Import collection

1. Mở Postman.
2. Bấm nút **Import** (góc trên trái).
3. Chọn tab **File** → **Upload Files**.
4. Chọn file:

   ```text
   w3\postman_collection.json
   ```

5. Bấm **Import**.

Sau khi import, sẽ có collection tên **“INT3505 W3 REST API Demo”**.

### 5.2. Gửi request trong Postman

Các request đã được cấu hình sẵn:

- **Health Check**
  - `GET http://localhost:5004/api/v1/health-check`

- **Books - List all**
  - `GET http://localhost:5004/api/v1/books`

- **Books - List by author**
  - `GET http://localhost:5004/api/v1/books?author=Robert%20C.%20Martin`

- **Books - Create**
  - `POST http://localhost:5004/api/v1/books`
  - Tab **Body**: `raw` + `JSON` với nội dung mẫu đã điền.

- **Books - Get by id**
  - `GET http://localhost:5004/api/v1/books/1`

- **Books - Update (PUT)**
  - `PUT http://localhost:5004/api/v1/books/1`
  - Tab **Body**: `raw` + `JSON` với nội dung cập nhật.

- **Books - Delete**
  - `DELETE http://localhost:5004/api/v1/books/1`

Chỉ cần chọn từng request trong collection, bấm **Send** để test.

---

## 6. Ghi chú về thiết kế REST

- **Naming conventions**:
  - Dùng **danh từ số nhiều**: `books`.
  - Tất cả **lowercase**.
  - Dùng **hyphen** để nối từ: `health-check`.
- **Versioning**:
  - Base path có version: `/api/v1/...` → dễ nâng cấp lên `/api/v2`.
- **Extensibility**:
  - Hàm `create_app()` giúp dễ dàng thêm blueprint, middleware, config mới.
  - Dễ mở rộng thêm resource khác (ví dụ: `authors`, `categories`) với cùng pattern URL.

