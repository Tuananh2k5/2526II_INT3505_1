# Demo TypeSpec

Thư mục này chứa file `main.tsp` định nghĩa một API Quản lý Thư viện đơn giản bằng ngôn ngữ TypeSpec của Microsoft.

TypeSpec cho phép module hóa rất cao và đóng vai trò như một ngôn ngữ thiết kế API (API design language) đích thực. File code TypeSpec có thể biên dịch (compile) thành JSON Schema, OpenAPI và vài định dạng khác chuẩn xác.

## Tính năng
- Dùng cú pháp tương tự TypeScript (bớt dài dòng hơn chuẩn YAML).
- Hệ sinh thái tool thông minh và import linh hoạt. Hoàn thiện cho kiến trúc API quy mô lớn.

## Demo: Sinh code (Biên Dịch Ra OpenAPI)
Để thí điểm quá trình biên dịch tài liệu quy chuẩn TypeSpec thành file chỉ dẫn OpenAPI v3 chi tiết:

1. Thiết lập các dependencies bằng npm:
```bash
npm install
```

2. Compile mã nguồn file định dạng TypeSpec cùng sự hỗ trợ của bộ OpenAPI3 emitter:
```bash
npx tsp compile . --emit @typespec/openapi3
```

Chạy command này sẽ xuất thư mục kết quả `tsp-output/` mang chứa file thông số `openapi.yaml`. Có file chuẩn này, bạn dễ dàng tiếp tục chạy OpenAPI Generator như thường lệ nhằm thiết lập mã nguồn boilerplate SDK/Server theo yêu cầu chuyên biệt.
