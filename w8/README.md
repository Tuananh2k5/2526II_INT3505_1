# Hướng dẫn Kiểm thử API (API Testing & QA)

Dự án này là một API quản lý Sản phẩm (Product Management API) cơ bản được xây dựng bằng Flask, sử dụng cấu trúc dữ liệu lưu trong bộ nhớ (in-memory) nhằm mục đích học tập và thực hành các kỹ thuật Kiểm thử phần mềm (QA).

## 1. Cài đặt môi trường

Để chạy dự án, bạn cần tạo môi trường ảo và cài đặt các thư viện cần thiết. Mở terminal và chạy các lệnh sau:

**Tạo môi trường ảo (Virtual Environment):**
```bash
python -m venv .venv
```

**Kích hoạt môi trường ảo:**
- Trên Windows:
  ```cmd
  .venv\Scripts\activate
  ```
- Trên macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

**Cài đặt các gói phụ thuộc:**
```bash
pip install -r requirements.txt
```

## 2. Chạy ứng dụng

Sau khi cài đặt xong, khởi động server Flask bằng lệnh:
```bash
python app.py
```
API của bạn sẽ chạy tại địa chỉ: `http://127.0.0.1:5000`

## 3. Hướng dẫn Test

### 3.1 Unit và Integration Testing (với pytest)
Để chạy bộ test tự động kiểm tra logic của từng endpoint, sử dụng `pytest`.

Mở một terminal mới (nhớ activate môi trường ảo) và chạy lệnh:
```bash
pytest tests/
```
Hoặc để xem kết quả chi tiết cho từng test case:
```bash
pytest -v tests/
```

### 3.2 Performance/Load Testing (với Locust)
Để kiểm tra khả năng chịu tải của API, chúng ta sử dụng `Locust`.

Chạy lệnh sau trong terminal:
```bash
locust -f locustfile.py
```
- Sau đó, mở trình duyệt và truy cập `http://localhost:8089`.
- Nhập số lượng người dùng đồng thời (Number of users) và tốc độ sinh user mới (Spawn rate).
- Đặt Host là `http://127.0.0.1:5000` và nhấn **Start swarming**.
- Bạn có thể xem các chỉ số thực tế như **Response Time (ms)** và **Error Rate (%)** trên giao diện web.

### 3.3 Integration & Reporting (với Postman & Newman)
Postman collection đã có sẵn kịch bản test (Tests tab). Để tự động hóa và xuất báo cáo HTML, ta dùng Newman.

**Cài đặt Newman và HTML Reporter:** (Yêu cầu phải có Node.js)
```bash
npm install -g newman newman-reporter-htmlextra
```

**Chạy Postman Collection và sinh báo cáo:**
```bash
newman run postman_collection.json -r cli,htmlextra
```
Sau khi chạy xong, một thư mục `newman` sẽ được tạo ra trong thư mục hiện tại. Bạn chỉ cần mở tệp `.html` bên trong thư mục đó bằng trình duyệt để xem báo cáo test chi tiết, trực quan.

## 4. Tại sao lại làm như vậy? (The "Why")

- **Sự khác biệt giữa Unit, Integration và Performance Testing:**
  - **Unit Testing:** Kiểm tra các thành phần, hàm nhỏ lẻ một cách độc lập (tuy nhiên trong Flask, ranh giới Unit/Integration thường mờ nhạt do ta test luôn cả logic định tuyến).
  - **Integration Testing:** Kiểm tra xem các thành phần có hoạt động trơn tru với nhau không (ví dụ: gửi request từ Client -> qua Router của Flask -> xử lý logic Controller -> trả về JSON hợp lệ).
  - **Performance Testing:** Đánh giá sức chịu đựng của hệ thống khi có nhiều người dùng truy cập cùng lúc. Một API có thể chạy đúng logic nhưng lại "sập" khi có lượng lớn người dùng.
- **Tại sao phải tự động hóa Postman test với Newman?**
  Thay vì phải bấm "Send" thủ công từng API, Newman cho phép ta đưa toàn bộ kịch bản test vào luồng CI/CD để chạy tự động mỗi khi có code mới.
- **Giá trị của Báo cáo HTML trực quan (HTML Reports):**
  Báo cáo trực quan từ `htmlextra` giúp team QA, Developer và cả Project Manager dễ dàng nhìn thấy bức tranh tổng thể: bao nhiêu test pass/fail, lỗi xảy ra ở đâu, từ đó đưa ra quyết định phát hành sản phẩm nhanh chóng hơn việc đọc log console khô khan.
- **Tại sao phải giám sát Error Rates và Response Times?**
  Trải nghiệm người dùng phụ thuộc rất nhiều vào tốc độ phản hồi. Nếu Response Time chậm, người dùng sẽ rời đi. Nếu Error Rate tăng đột biến, hệ thống có thể đang gặp sự cố nghiêm trọng cần khắc phục ngay lập tức để tránh thiệt hại.
