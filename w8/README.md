# Hướng dẫn Kiểm thử API (API Testing & QA)

Dự án này là một API quản lý Sản phẩm (Product Management API) cơ bản được xây dựng bằng Flask, sử dụng cấu trúc dữ liệu lưu trong bộ nhớ (in-memory) nhằm mục đích học tập và thực hành các kỹ thuật Kiểm thử phần mềm (QA).

---

## 0. Cấu trúc dự án & Chức năng các file

```
w8/
├── app.py                    # File chính: Định nghĩa Flask app và toàn bộ các REST API endpoint
├── locustfile.py             # Kịch bản load testing: Mô phỏng hành vi người dùng ảo
├── postman_collection.json   # Bộ kịch bản test Postman: Các request + assertion tự động
├── requirements.txt          # Danh sách thư viện Python cần cài đặt
├── tests/
│   ├── __init__.py           # File khởi tạo package (để pytest nhận diện thư mục tests/)
│   └── test_app.py           # Bộ test tự động: Toàn bộ Unit/Integration test bằng pytest
└── newman/                   # Thư mục tự động sinh ra sau khi chạy Newman, chứa báo cáo HTML
```

### Chi tiết từng file

| File | Vai trò | Công nghệ |
|---|---|---|
| `app.py` | Server API chính, xử lý 5 endpoint CRUD cho Product | Flask |
| `tests/test_app.py` | 9 test case kiểm tra logic từng endpoint (happy path & edge case) | pytest |
| `locustfile.py` | Định nghĩa user ảo với 3 loại task có trọng số để mô phỏng tải | Locust |
| `postman_collection.json` | Collection gồm các request + script kiểm tra response tự động | Postman / Newman |
| `requirements.txt` | Khai báo phiên bản cố định: Flask 3.0.3, pytest 8.1.1, locust 2.24.1 | pip |

#### `app.py` — Flask API Server

File định nghĩa **5 REST endpoint** hoạt động trên dữ liệu in-memory (list Python):

| Method | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/api/products` | Lấy toàn bộ danh sách sản phẩm |
| `GET` | `/api/products/<id>` | Lấy một sản phẩm theo ID |
| `POST` | `/api/products` | Tạo sản phẩm mới (validate đủ field & kiểu dữ liệu) |
| `PUT` | `/api/products/<id>` | Cập nhật một phần thông tin sản phẩm |
| `DELETE` | `/api/products/<id>` | Xóa sản phẩm, trả về `204 No Content` |

#### `tests/test_app.py` — Bộ Test tự động

File chứa **9 test case** bao phủ đầy đủ các scenario:

| Test case | Mục đích |
|---|---|
| `test_get_all_products` | Kiểm tra GET trả về đúng 2 sản phẩm mặc định |
| `test_get_specific_product` | Kiểm tra GET theo ID trả đúng tên sản phẩm |
| `test_get_product_not_found` | Kiểm tra GET ID không tồn tại trả về `404` |
| `test_create_product` | Kiểm tra POST tạo đúng sản phẩm với ID tự tăng |
| `test_create_product_missing_fields` | Kiểm tra POST thiếu field bắt buộc trả về `400` |
| `test_update_product` | Kiểm tra PUT cập nhật đúng giá trị |
| `test_update_product_not_found` | Kiểm tra PUT ID không tồn tại trả về `404` |
| `test_delete_product` | Kiểm tra DELETE thành công và sản phẩm biến mất |
| `test_delete_product_not_found` | Kiểm tra DELETE ID không tồn tại trả về `404` |

#### `locustfile.py` — Kịch bản Load Test

File định nghĩa **1 lớp người dùng ảo** (`ProductAPIUser`) với **3 loại task** mang trọng số khác nhau:

| Task | Trọng số | Hành vi |
|---|---|---|
| `view_products` | 4 | Gọi `GET /api/products` — tần suất cao nhất (chiếm 4/7 ≈ 57%) |
| `view_single_product` | 2 | Gọi `GET /api/products/{id}` với id ngẫu nhiên (1 hoặc 2) |
| `create_product` | 1 | Gọi `POST /api/products` với dữ liệu ngẫu nhiên (tần suất thấp nhất) |

Mỗi user ảo chờ **1–3 giây** ngẫu nhiên giữa các lần gọi (`wait_time = between(1, 3)`).

---

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

---

## 2. Chạy ứng dụng

Sau khi cài đặt xong, khởi động server Flask bằng lệnh:
```bash
python app.py
```
API của bạn sẽ chạy tại địa chỉ: `http://127.0.0.1:5000`

---

## 3. Hướng dẫn Test

### 3.1 Unit và Integration Testing (với pytest)

#### Cơ chế hoạt động

`pytest` là framework kiểm thử Python. Khi chạy, nó tự động:
1. **Khám phá** tất cả file có tên dạng `test_*.py` trong thư mục `tests/`.
2. **Thiết lập môi trường test (Fixtures):** Trước mỗi test case, hai fixture sẽ chạy tự động:
   - `client`: Tạo một **Flask Test Client** giả lập — cho phép gửi HTTP request trực tiếp đến app mà **không cần mở cổng mạng thật**, giúp test chạy nhanh và tách biệt hoàn toàn với môi trường production.
   - `reset_data` (autouse): **Khôi phục dữ liệu in-memory về trạng thái ban đầu** (2 sản phẩm: Laptop, Mouse) và reset `next_id = 3` sau mỗi test. Điều này đảm bảo mỗi test case độc lập, không bị ảnh hưởng bởi test trước.
3. **Thực thi** từng hàm `test_*`, gửi request qua `client`, so sánh kết quả thực tế với kết quả mong đợi bằng lệnh `assert`.
4. **Báo cáo** kết quả pass/fail ra terminal.

#### Chạy test

Mở một terminal mới (nhớ activate môi trường ảo) và chạy lệnh:
```bash
pytest tests/
```
Hoặc để xem kết quả chi tiết cho từng test case:
```bash
pytest -v tests/
```

**Ví dụ output khi thành công:**
```
tests/test_app.py::test_get_all_products          PASSED
tests/test_app.py::test_get_specific_product      PASSED
tests/test_app.py::test_get_product_not_found     PASSED
...
9 passed in 0.25s
```

---

### 3.2 Performance/Load Testing (với Locust)

#### Cơ chế hoạt động

Locust mô phỏng nhiều người dùng thật đồng thời gửi request đến API theo kịch bản đã định nghĩa trong `locustfile.py`:

1. **Khởi động:** Lệnh `locust -f locustfile.py` khởi động Locust Master và mở giao diện web quản lý tại `http://localhost:8089`.
2. **Cấu hình test:** Trên giao diện web, bạn nhập:
   - **Number of users:** Tổng số người dùng ảo cần mô phỏng (VD: 100 users).
   - **Spawn rate:** Số user được tạo mới **mỗi giây** cho đến khi đạt đủ số lượng (VD: 10 users/s → mất 10 giây để đạt 100 users).
   - **Host:** Địa chỉ server cần test — đặt là `http://127.0.0.1:5000`.
3. **Thực thi:** Mỗi user ảo liên tục lặp vòng — chọn task theo trọng số → gửi request → chờ 1–3 giây → lặp lại. Các task được phân bổ: ~57% `GET /api/products`, ~29% `GET /api/products/{id}`, ~14% `POST /api/products`.
4. **Giám sát real-time:** Dashboard web hiển thị trực tiếp:
   - **RPS (Requests/sec):** Số request mỗi giây hệ thống đang xử lý.
   - **Response Time (ms):** Thời gian phản hồi trung bình, trung vị (p50), p95, p99.
   - **Failure %:** Tỷ lệ request bị lỗi.
   - **Charts:** Biểu đồ thay đổi theo thời gian thực.

Chạy lệnh sau trong terminal:
```bash
locust -f locustfile.py
```
- Sau đó, mở trình duyệt và truy cập `http://localhost:8089`.
- Nhập số lượng người dùng đồng thời (Number of users) và tốc độ sinh user mới (Spawn rate).
- Đặt Host là `http://127.0.0.1:5000` và nhấn **Start swarming**.
- Bạn có thể xem các chỉ số thực tế như **Response Time (ms)** và **Error Rate (%)** trên giao diện web.

---

### 3.3 Integration & Reporting (với Postman & Newman)

#### Cơ chế hoạt động

Postman và Newman tách biệt nhau theo hai giai đoạn:

1. **Postman (thiết kế kịch bản):** File `postman_collection.json` chứa các request đã được thiết kế sẵn, mỗi request có thêm **tab "Tests"** — là các đoạn script JavaScript nhỏ chạy sau khi nhận response, kiểm tra (assert) các điều kiện như `status code`, cấu trúc JSON, giá trị cụ thể.

2. **Newman (thực thi tự động):** Newman là CLI runner của Postman. Thay vì mở UI Postman bấm "Send" thủ công từng request, Newman đọc file `postman_collection.json`, gửi toàn bộ request theo thứ tự, chạy tất cả script kiểm tra, và thu thập kết quả.

3. **Reporter `htmlextra` (sinh báo cáo):** Sau khi Newman thực thi xong, `newman-reporter-htmlextra` tổng hợp kết quả thành một file HTML trực quan, hiển thị: danh sách request pass/fail, thời gian thực thi, nội dung request/response, chi tiết lỗi assertion. File báo cáo được lưu vào thư mục `newman/`.

**Luồng thực thi:**
```
postman_collection.json
        │
        ▼
    Newman CLI  ──────►  Gửi HTTP request đến Flask API (http://127.0.0.1:5000)
        │                        │
        │                        ▼
        │              Chạy Test Scripts (JS assertions)
        │
        ▼
newman-reporter-htmlextra  ──►  newman/*.html  (Báo cáo trực quan)
```

**Cài đặt Newman và HTML Reporter:** (Yêu cầu phải có Node.js)
```bash
npm install -g newman newman-reporter-htmlextra
```

**Chạy Postman Collection và sinh báo cáo:**
```bash
newman run postman_collection.json -r cli,htmlextra
```
Sau khi chạy xong, một thư mục `newman` sẽ được tạo ra trong thư mục hiện tại. Bạn chỉ cần mở tệp `.html` bên trong thư mục đó bằng trình duyệt để xem báo cáo test chi tiết, trực quan.

---

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
