# Demo OpenAPI

Thư mục này chứa file `openapi.yaml` định nghĩa một API Quản lý Thư viện đơn giản.

## Công cụ
- **Swagger UI**: Dùng để hiển thị và xem tài liệu API.
- **OpenAPI Generator**: Dùng để sinh source code (code generation) tự động.

## Demo: Sinh Code (Code Generation)
Để thử nghiệm việc tự động tạo một server NodeJS Express từ định nghĩa API này, hãy chạy lệnh sau bằng `npx`:

```bash
npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g nodejs-express-server -o ./generated-server
```

Lệnh này sẽ phân tích file `openapi.yaml` và tự động tạo ra một server Node.js Express hoàn chỉnh bên trong thư mục `generated-server`. Sau đó, bạn có thể khởi chạy server này theo hướng dẫn bên trong để thử nghiệm các request.
