# Buổi 6: Authentication và Authorization (Flask Backend)

Backend cơ bản triển khai bằng Flask đáp ứng các yêu cầu thực hành của Buổi 6 về Web Security (JWT, Authentication & Authorization).

## 1. So sánh JWT vs OAuth 2.0

*   **JWT (JSON Web Token):** Là một *định dạng* token dùng để truyền tải thông tin an toàn giữa các bên dưới dạng JSON object. Thường dùng cho việc xác thực (Authentication - Client là ai) trong kiến trúc stateless (server không cần phải lưu trữ session).
*   **OAuth 2.0:** Là một *giao thức/framework* ủy quyền (Authorization - Client được làm gì). Cho phép ứng dụng bên thứ 3 truy cập tài nguyên mà không cần trực tiếp chia sẻ thông tin đăng nhập (như mật khẩu). OAuth 2.0 thường *sử dụng* JWT để làm định dạng cho token truy cập (Access Token).

## 2. Các khái niệm cơ bản

*   **Bearer Token:** Loại token mà bất kỳ ai nắm giữ ("bearer") đều có thể sử dụng (giống như tiền mặt). Do đó, token này luôn phải được bảo vệ nghiêm ngặt (truyền qua HTTPS, lưu trữ an toàn).
*   **Refresh Token:** Token đặc biệt có thời hạn sống dài, dùng để đổi lấy Access Token mới khi Access Token cũ hết hạn. Cơ chế này giúp người dùng không phải đăng nhập lại liên tục trong khi vẫn thu ngắn được tuổi thọ của Access Token (để giảm thiểu hậu quả nếu Access Token bị lộ).
*   **Roles:** Vai trò của thực thể trong hệ thống (ví dụ: `admin`, `user`). Dùng để phân quyền truy cập tới chức năng, endpoint.
*   **Scopes:** Phạm vi quyền hạn chi tiết (ví dụ: `read`, `write`, `delete`). Dùng để giới hạn việc truy cập, thay đổi tài nguyên ở cấp độ hành động.

## 3. Triển khai API bằng Flask

### Cài đặt môi trường

1.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```

### Chạy ứng dụng

2.  Khởi động server Flask:
    ```bash
    python app.py
    ```
    Server sẽ mặc định chạy tại `http://127.0.0.1:5000`.

### Các endpoints chính:

*   `POST /login`: Nhận payload JSON `{ "username": "admin", "password": "password123" }` (hoặc `user1`). Trả về `access_token` và `refresh_token`.
*   `POST /refresh`: Nhận `{ "refresh_token": "<token_ở_trên>" }` để cấp lại `access_token` mới khi phiên bản cũ hết hạn.
*   `GET /protected`: Yêu cầu gửi kèm Header `Authorization: Bearer <access_token>`. Trả về thông tin user, roles, scopes hiện tại.
*   `GET /admin-only`: Yêu cầu token hợp lệ CÓ role là `admin`.
*   `POST /write-data`: Yêu cầu token hợp lệ CÓ chứa scope `write`.

## 4. Security Audit và Đề xuất khắc phục rủi ro

### Rủi ro 1: Token Leakage (Lộ Token qua XSS hoặc URL)
*   **Phát hiện:** Dự án mẫu cung cấp endpoint `/insecure-login` (có thể rò rỉ token qua URL params nếu được gọi bằng GET, khi đó nó được lưu trong lịch sử trình duyệt hoặc log máy chủ proxy). Ngoài ra, nếu ứng dụng frontend lưu JWT vào `localStorage`, nó có nguy cơ bị lộ khi bị tấn công XSS.
*   **Khắc phục đề xuất:**
    *   Sử dụng phương thức `POST` và truyền token qua vùng Header HTTP (ví dụ: `Authorization: Bearer <token>`) thay vì URL parameter.
    *   Lưu trữ token ở `HttpOnly Cookies` thay vì `localStorage` với các dự án Web. Cookies này không thể bị truy cập bằng Javascript trên trình duyệt, nhờ đó miễn nhiễm với hình thức tấn công XSS lấy cắp token.
    *   Bắt buộc luôn sử dụng HTTPS trên kết nối thực tế.

### Rủi ro 2: Replay Attack (Tấn công phát lại)
*   **Phát hiện:** Kẻ gian bắt được token và gửi lại request cũ được đính kèm token (nếu token có thời hạn sống quá lâu và dùng trên đường truyền không đính mã hoá HTTPS).
*   **Khắc phục đề xuất:**
    *   Sử dụng Access Token có tuổi thọ (expiration `exp`) rất ngắn (ví dụ: 5 - 15 phút).
    *   Sử dụng cơ chế Refresh Token để tự động đổi phiên đăng nhập một cách mượt mà mà không ảnh hưởng tới trải nghiệm người dùng, mã trong `app.py` đã ứng dụng cách này với `access_token` ngắn hạn và `refresh_token` dài hạn hơn.
    *   Chặn đường bắt gói tin ở mạng trung gian bằng cách sử dụng HTTPS để tạo đường hầm mã hóa (SSL/TLS).
