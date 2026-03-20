# Hướng Dẫn Sử Dụng Book Manager API Đã Triển Khai Trên Vercel

Dự án này đã được triển khai (deploy) thành công lên nền tảng Vercel. Bạn có thể tương tác trực tiếp với API công khai mà không cần chạy máy chủ cục bộ (localhost).

## Các Link Quan Trọng

- **Trang chủ & Kiểm tra trạng thái:** [https://w4-liard.vercel.app](https://w4-liard.vercel.app/)
  Truy cập link này để nhận thông báo mặc định của dự án để đảm bảo server vẫn hoạt động bình thường.

- **Tài Liệu Swagger UI (Thử nghiệm API):** [https://w4-liard.vercel.app/docs](https://w4-liard.vercel.app/docs)
  Nơi chứa toàn bộ tài liệu OpenAPI. Tại đây, bạn có thể xem các endpoint và dễ dàng thử nghiệm các thao tác CRUD (Thêm, Đọc, Sửa, Xóa) trực tiếp trên trình duyệt.

- **Cấu trúc OpenAPI (YAML):** [https://w4-liard.vercel.app/openapi.yaml](https://w4-liard.vercel.app/openapi.yaml)
  Tệp cấu hình đặc tả các API mà bạn đã định nghĩa.

## Danh Sách Các Endpoints API Phổ Biến

Dưới đây là các đường dẫn được cấu hình đầy đủ. Bạn cũng có thể thiết lập các phần mềm HTTP Client như Postman, Insomnia hoặc Fetch/Axios (JavaScript) để test trực tiếp.

### 📚 Quản Lý Sách (Books)
- **Lấy danh sách (GET):** `https://w4-liard.vercel.app/api/books`
- **Tạo sách mới (POST):** `https://w4-liard.vercel.app/api/books`
- **Chi tiết 1 quyển sách (GET):** `https://w4-liard.vercel.app/api/books/<book_id>`
- **Cập nhật sách (PUT):** `https://w4-liard.vercel.app/api/books/<book_id>`
- **Xóa sách (DELETE):** `https://w4-liard.vercel.app/api/books/<book_id>`

*(Định dạng Payload `POST` & `PUT`: cần có các trường `"title"`, `"author"`, `"year"`)*

### ✍️ Quản Lý Tác Giả (Authors)
- **Lấy danh sách (GET):** `https://w4-liard.vercel.app/api/authors`
- **Tạo tác giả mới (POST):** `https://w4-liard.vercel.app/api/authors`
- **Chi tiết 1 tác giả (GET):** `https://w4-liard.vercel.app/api/authors/<author_id>`
- **Cập nhật tác giả (PUT):** `https://w4-liard.vercel.app/api/authors/<author_id>`
- **Xóa tác giả (DELETE):** `https://w4-liard.vercel.app/api/authors/<author_id>`

*(Định dạng Payload `POST` & `PUT`: cần các trường `"name"`)*

## Lưu Ý Về Dữ Liệu
Vì ứng dụng sử dụng cấu trúc lưu trữ dữ liệu In-Memory (lưu dữ liệu trên Ram thông qua Dictionary của Python), mỗi khi môi trường Serverless Function trên Vercel tự động khởi động (cold-start) dữ liệu sẽ được reset (làm mới) trở về trạng thái Seed ban đầu (với 2 data sách & tác giả mặc định).
