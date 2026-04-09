# RESTful API Flask (Week 6)

## Tổng quan dự án

Dự án này là một API RESTful được xây dựng bằng Flask nhằm trình diễn các best practice trong bảo mật và authentication. Dự án bao gồm các hệ thống: Registration, Login (JWT với access token và refresh token thông qua HttpOnly cookie), Refresh token rotation để chặn Replay attack, Phân quyền người dùng theo Model RBAC (Roles) lẫn Scope-based, và tài liệu hóa qua Swagger UI.

### So sánh JWT và OAuth 2.0
- **JWT (JSON Web Token):** Là một định dạng token (gọn nhẹ và an toàn). JWT tự mang theo thông tin xác thực (như `sub`, `roles`, `scopes`) và chữ ký (signature) bên trong chính bản thân nó thay vì lưu trạng thái tại server.  
- **OAuth 2.0:** Là một khung (framework) ủy quyền xác định luồng giao tiếp giữa client, resource server và authorization server, cho phép ứng dụng bên thứ ba truy cập tài nguyên (ví dụ app của bạn dùng Google Account để login) thông qua các `scopes`. OAuth 2.0 thường dùng JWT làm định dạng cho Access Token.

---

## Tính năng

1. **Authentication:** 
    - Đăng ký và Đăng nhập bảo mật sử dụng mật khẩu mã hóa (bcrypt).
    - Session-less nhưng an toàn qua **JWT**.
    - Cấp **Access Token** ngắn hạn (10 phút) gửi về cho client qua JSON.
    - Cấp **Refresh Token** dài hạn (7 ngày), an toàn hơn bằng cách lưu giữ tại cookie `HttpOnly` (chống lộ mã qua XSS).
    - Endpoint `/refresh` cấp cặp token mới và tự động hủy bỏ (revoke) JTI của token cũ chống replay.

2. **Authorization (RBAC & Scope-based):**
    - Kiểm soát theo Role (VD như `admin` có quyền xóa tài nguyên).
    - Kiểm soát theo Scopes trên token cấp phát (`read:item`, `write:item`).

3. **Resources (CRUD for Item):**
    - `GET /items`: Lấy danh sách có hỗ trợ phân trang (`page`, `per_page`).
    - `POST /items`: Tạo item mới.
    - `GET /items/<id>`, `PUT /items/<id>`, `DELETE /items/<id>` (yêu cầu quyền Admin cho DELETE).

4. **Security Best Practices:**
    - Không lưu thông tin nhạy cảm vào JWT payload.
    - Chữ ký trên JWT được ký thông qua thuật toán mạnh (HS256).
    - Tính năng thiết lập Blocklist thu hồi mã khi user đăng xuất, nhằm bảo đảm Token hết hiệu lực.

5. **Tài liệu & Test (Swagger UI):**
    - Có sẵn Swagger UI ở `/apidocs`.

---

## Hướng dẫn sử dụng

### 1. Cài đặt Python Dependencies
Mở Terminal, đi tới thư mục `w6` và cài đặt các gói yêu cầu:
```bash
cd w6
pip install -r requirements.txt
```

### 2. Tạo Migrations và khởi tạo Database
Khởi tạo cơ sở dữ liệu SQLite trong thư mục dự án:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. Chạy server
Khởi động ứng dụng Flask:
```bash
python app.py
```
> Hoặc chạy qua lệnh Flask:  
> `flask --app app.py run -p 8000`

### 4. Kiểm thử với Swagger UI
Mở trình duyệt lên và đi tới địa chỉ: [http://127.0.0.1:8000/apidocs](http://127.0.0.1:8000/apidocs) để tương tác trực diện qua Swagger.

Quy trình Test:
- **Đăng ký**: Tạo một user thông qua Swagger form `/register`. (Nhập tuỳ chọn scopes là `["read:item", "write:item"]`, nhập role `admin` nếu muốn test tính năng xóa).
- **Đăng nhập**: Ở endpoint `/login` điền thông tin đăng nhập, nó sẽ trả về `access_token` và gài `refresh_token` vào HttpOnly Cookie.
- **Ủy quyền Swagger**: Lấy chuỗi `access_token` copy vào nút "**Authorize**" bằng việc nhập giá trị: `Bearer <token_vừa_copy>`. Mọi API khác bạn gọi sẽ tự đưa mã này lên header.
- **Thao tác `/items`**: Gọi list, get, post, put, delete tuỳ theo scope/role.
- **Xoay tua khóa `/refresh`**: Cookie (HttpOnly) có chứa Refresh token. Nếu bạn gọi endpoint `/refresh`, server sẽ đọc Cookie, cấp phát Tokens mới và blacklist token cũ.
