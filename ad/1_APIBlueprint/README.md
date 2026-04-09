# Demo API Blueprint

Thư mục này chứa file `api.apib` định nghĩa một API Quản lý Thư viện đơn giản. Điểm nổi bật của API Blueprint là cách tiếp cận tĩnh siêu đơn giản dựa trên Markdown.

## Công cụ
- **Aglio**: Đầu ra (renderer) API Blueprint thành giao diện web với Node.js.
- **Dredd**: Một framework kiểm thử (testing) HTTP API độc lập không phụ thuộc ngôn ngữ.

## Demo: Tự động tạo Tài liệu
Để kết xuất (render) file API này thành một file HTML tĩnh và xem trên trình duyệt web:

```bash
npm install -g aglio
aglio -i api.apib -o index.html
```

## Demo: Kiểm thử (Testing / Verification)
Để test tự động xem một server đang chạy có phản hồi đúng các logic như tài liệu mô tả hay không, bạn có thể chạy Dredd:

```bash
npm install -g dredd
dredd api.apib http://localhost:3000/api
```
