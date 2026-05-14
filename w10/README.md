# 🛡️ Flask Demo: Service Operation – Security & Monitoring

> **Môn học:** INT3505 – Vận hành Dịch vụ Phần mềm  
> **Chủ đề:** Security & Monitoring trong môi trường Production  
> **Stack:** Python · Flask · structlog · Prometheus · Flask-Limiter · pybreaker

---

## 📖 Giới thiệu

Project này là một ứng dụng Flask mẫu minh họa bốn kỹ thuật quan trọng trong vận hành dịch vụ thực tế:

| Tính năng | Thư viện | Mục đích |
|---|---|---|
| **Structured Logging** | `structlog` + `logging` | Ghi log có cấu trúc ra console & file |
| **Monitoring / Metrics** | `prometheus_flask_exporter` | Expose metrics tại `/metrics` cho Prometheus scrape |
| **Rate Limiting** | `Flask-Limiter` | Ngăn chặn spam / brute-force (5 req/phút) |
| **Circuit Breaker** | `pybreaker` | Tự động "ngắt mạch" khi external service liên tục lỗi |

---

## 📂 Cấu trúc Project

```
w10/
├── app.py           ← Toàn bộ logic ứng dụng (có comment chi tiết)
├── requirements.txt ← Danh sách thư viện cần cài
├── app.log          ← File log (tự tạo khi chạy app)
└── README.md        ← Tài liệu này
```

---

## ⚙️ Hướng dẫn Khởi tạo & Cài đặt

### Bước 1 – Tạo môi trường ảo `.venv`

```bash
# Di chuyển vào thư mục project
cd w10

# Tạo virtual environment
python -m venv .venv
```

### Bước 2 – Kích hoạt môi trường ảo

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

> Sau khi kích hoạt, terminal sẽ hiển thị `(.venv)` ở đầu dòng lệnh.

### Lưu ý cho VS Code (Fix lỗi "Cannot find module")
Nếu bạn thấy cảnh báo `Cannot find module 'pybreaker'` hoặc các thư viện khác trong VS Code (Pylance):
1. Nhấn `Ctrl + Shift + P`.
2. Gõ `Python: Select Interpreter`.
3. Chọn đường dẫn có chứa `(.venv)` (ví dụ: `.\.venv\Scripts\python.exe`).

### Bước 3 – Cài đặt thư viện từ `requirements.txt`

```bash
pip install -r requirements.txt
```

### Bước 4 – Chạy ứng dụng

```bash
python app.py
```

Kết quả mong đợi trên console:

```
2026-05-14T10:45:00 | INFO     | app_starting host=0.0.0.0 port=5000 debug=True
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

---

## 🗺️ Danh sách Endpoints

| Method | Path | Mô tả |
|---|---|---|
| `GET` | `/` | Trang chủ, liệt kê tất cả endpoint |
| `GET` | `/api/data` | Endpoint bình thường, minh họa logging |
| `GET` | `/api/secure` | Endpoint có **Rate Limit** (5 req/phút) |
| `GET` | `/api/external` | Endpoint có **Circuit Breaker** (lỗi 80%) |
| `GET` | `/metrics` | **Prometheus** metrics (raw text) |

---

## 🧪 Hướng dẫn Test Từng Tính năng

### 1. 📋 Logging – Xem log request trong thời gian thực

**Mở 2 terminal song song:**

- Terminal 1: chạy app → `python app.py`
- Terminal 2: gọi API

```bash
# Gọi trang chủ
curl http://localhost:5000/

# Gọi endpoint data
curl http://localhost:5000/api/data
```

**Kết quả mong đợi trên console (Terminal 1):**
```
2026-05-14T10:46:01 | INFO | request_started ip=127.0.0.1 method=GET path=/api/data
2026-05-14T10:46:01 | INFO | api_data_called  ip=127.0.0.1 method=GET
2026-05-14T10:46:01 | INFO | request_finished ip=127.0.0.1 method=GET path=/api/data status=200 duration_ms=1.23
```

**Xem nội dung file log:**
```bash
# Windows
type app.log

# macOS / Linux
cat app.log
# hoặc theo dõi live:
tail -f app.log
```

> ✅ **Quan sát:** Mỗi request đều được ghi đầy đủ: IP, method, path, status code, và thời gian xử lý (ms). Log được lưu cả ở console lẫn file `app.log`.

---

### 2. 📊 Monitoring – Prometheus Metrics

```bash
curl http://localhost:5000/metrics
```

**Kết quả mong đợi (raw Prometheus format):**
```
# HELP flask_http_request_duration_seconds Flask HTTP request duration in seconds
# TYPE flask_http_request_duration_seconds histogram
flask_http_request_duration_seconds_bucket{le="0.005",method="GET",path="/",status="200"} 1.0
...
# HELP app_info Application information
# TYPE app_info gauge
app_info{environment="demo",version="1.0.0"} 1.0
```

**Gọi vài endpoint trước, rồi kiểm tra metrics để thấy số lượng request:**
```bash
curl http://localhost:5000/api/data
curl http://localhost:5000/api/data
curl http://localhost:5000/api/data
curl http://localhost:5000/metrics
```

Tìm dòng `flask_http_request_total` – sẽ thấy counter tăng lên theo số lần gọi.

> ✅ **Quan sát:** `prometheus_flask_exporter` tự động thu thập metrics cho tất cả endpoint (latency histogram, request counter, response size) mà không cần thêm code vào từng route.

---

### 3. 🚦 Rate Limiting – Chặn spam (5 req/phút)

**Gọi liên tục endpoint `/api/secure`:**

```bash
# Windows PowerShell – gọi 7 lần liên tiếp
1..7 | ForEach-Object { curl http://localhost:5000/api/secure; Write-Host "" }

# macOS / Linux – gọi 7 lần liên tiếp
for i in {1..7}; do curl -s http://localhost:5000/api/secure; echo; done
```

**Kết quả mong đợi:**
- Lần 1–5: HTTP `200 OK`
  ```json
  {"message": "Truy cập thành công vào endpoint được bảo vệ!", ...}
  ```
- Lần 6 trở đi: HTTP `429 Too Many Requests`
  ```json
  {
    "error": "Too Many Requests",
    "message": "Bạn đã vượt quá giới hạn request. Hãy thử lại sau 1 phút.",
    "retry_after": "60 seconds"
  }
  ```

**Kiểm tra log khi bị rate limit:**
```
2026-05-14T10:47:05 | WARNING | rate_limit_exceeded ip=127.0.0.1 path=/api/secure
```

> ✅ **Quan sát:** `Flask-Limiter` đếm số request theo IP. Khi vượt ngưỡng 5 req/phút, tự động trả về 429 và ghi cảnh báo vào log.

---

### 4. ⚡ Circuit Breaker – Ngắt mạch khi service lỗi liên tục

External service trong demo được cấu hình **lỗi 80%** để dễ kích hoạt circuit breaker.

**Gọi liên tục endpoint `/api/external`:**

```bash
# Windows PowerShell
1..10 | ForEach-Object { curl http://localhost:5000/api/external; Write-Host "" }

# macOS / Linux
for i in {1..10}; do curl -s http://localhost:5000/api/external; echo; done
```

**Ba giai đoạn của Circuit Breaker:**

#### Giai đoạn 1: CLOSED (Bình thường – đang đếm lỗi)
```json
{
  "status": "error",
  "circuit_breaker": "CLOSED (đang đếm lỗi...)",
  "message": "Lỗi kết nối tới external service: External service is unavailable!"
}
```
HTTP: `502 Bad Gateway`

#### Giai đoạn 2: OPEN (Sau 3 lỗi liên tiếp – đã ngắt mạch!)
```json
{
  "status": "error",
  "circuit_breaker": "OPEN (đã ngắt mạch!)",
  "message": "Service bên ngoài đang không khả dụng. Circuit Breaker đã kích hoạt.",
  "retry_after": "15 seconds"
}
```
HTTP: `503 Service Unavailable`

**Log khi circuit mở:**
```
2026-05-14T10:48:12 | WARNING | circuit_breaker_state_change breaker=external_service old=closed new=open
2026-05-14T10:48:13 | ERROR   | circuit_breaker_open ip=127.0.0.1 path=/api/external
```

#### Giai đoạn 3: HALF-OPEN (Sau 15 giây – tự thử lại)
Chờ 15 giây, circuit breaker chuyển sang trạng thái `HALF-OPEN`. Nếu lần thử tiếp theo thành công → đóng mạch lại (`CLOSED`).

```bash
# Chờ 15 giây rồi gọi lại
Start-Sleep 15  # PowerShell
# hoặc
sleep 15        # Linux/macOS

curl http://localhost:5000/api/external
```

> ✅ **Quan sát:** `pybreaker` hoạt động như một "cầu dao điện tự động". Sau 3 lỗi liên tiếp, nó ngắt hoàn toàn các request tới service lỗi (tránh cascade failure), rồi tự thử lại sau 15 giây.

---

## 🔬 Bảng Tóm tắt Test Cases

| Test Case | Endpoint | Cách test | Kết quả mong đợi |
|---|---|---|---|
| Log request bình thường | `/api/data` | `curl` 1 lần | Log xuất hiện ở console & `app.log` |
| Log đầy đủ fields | `/api/data` | Xem console | Có: timestamp, level, ip, method, path, status, duration_ms |
| Prometheus metrics | `/metrics` | `curl` sau vài request | Thấy counter và histogram tăng |
| Rate limit thành công | `/api/secure` | `curl` lần 1-5 | HTTP 200 |
| Rate limit bị chặn | `/api/secure` | `curl` lần 6+ | HTTP 429 + message tiếng Việt |
| Circuit Breaker đếm lỗi | `/api/external` | `curl` 1-2 lần | HTTP 502, trạng thái CLOSED |
| Circuit Breaker OPEN | `/api/external` | `curl` lần 4+ | HTTP 503, trạng thái OPEN |
| Circuit Breaker recovery | `/api/external` | Sau 15s | Circuit thử HALF-OPEN → có thể về CLOSED |

---

## 📝 Ghi chú

- **Rate Limit storage:** Mặc định dùng `memory://` (mất khi restart). Production nên dùng Redis: `storage_uri="redis://localhost:6379"`.
- **Circuit Breaker config:** `fail_max=3`, `reset_timeout=15s` – có thể chỉnh trong `app.py`.
- **Xác suất lỗi:** External service lỗi 80% (`random.random() < 0.8`) – có thể điều chỉnh để test nhanh hơn.
- **Log file:** `app.log` được rotate tự động khi đạt 5MB, giữ tối đa 3 file backup.
