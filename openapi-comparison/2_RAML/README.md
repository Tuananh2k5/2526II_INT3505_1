# Demo RAML

Thư mục này chứa file `api.raml` định nghĩa một API Quản lý Thư viện đơn giản. 

## Công cụ
- **raml2html**: Một bộ công cụ tạo tài liệu định dạng HTML đơn giản từ file thiết kế RAML.
- **osprey-mock-service**: Dùng để tạo nháp ứng dụng API giả lập (mock) bằng Node.js từ định nghĩa RAML.

## Demo: Tự động Tạo Tài liệu
Kết xuất file tài liệu RAML trên thành giao diện trang HTML:

```bash
npm install -g raml2html
raml2html api.raml > index.html
```

## Demo: Phục vụ Mock Server / Code Generation
Tạo rất nhanh một mô hình mock server bằng Osprey Mock Service để kiểm tra ngay lập tức các tương tác. Mock service sẽ xử lý định nghĩa kèm theo mẫu thông tin phản hồi của bạn, sau đó khởi chạy luôn giao diện mô phỏng một server:

```bash
npm install -g osprey-mock-service
osprey-mock-service -f api.raml -p 3000
```
