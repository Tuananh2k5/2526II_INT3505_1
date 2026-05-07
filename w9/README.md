# Payment API — Versioning Case Study
## API Versioning & Lifecycle Management (Flask)

---

## Cấu trúc thư mục

```
w9/
├── run.py                          # Entry point — chạy Flask server
├── requirements.txt                # Dependencies (flask>=3.0.0)
├── app/
│   ├── __init__.py                 # Application Factory
│   └── api/
│       ├── v1/
│       │   └── payments.py         # Blueprint v1 (DEPRECATED)
│       ├── v2/
│       │   └── payments.py         # Blueprint v2 (STABLE)
│       └── versioned/
│           └── payments.py         # Query Param Versioning (tham khảo)
└── docs/
    ├── MIGRATION_PLAN.md           # Kế hoạch migration 4 giai đoạn
    └── DEPRECATION_NOTICE.md       # Email thông báo deprecation
```

---

## Cài đặt & Chạy

```bash
# Bước 1: Tạo virtual environment
python -m venv venv

# Bước 2: Kích hoạt (Windows)
venv\Scripts\activate

# Bước 3: Cài dependencies
pip install -r requirements.txt

# Bước 4: Chạy server
python run.py
```

Server sẽ khởi động tại: `http://localhost:5000`

---

## Các Endpoint

### URL Versioning

#### API v1 (DEPRECATED)

```bash
# POST — Tạo giao dịch
curl -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-001",
    "amount": 150000,
    "payment_method": "card",
    "card_number": "4111111111111111"
  }'

# GET — Danh sách giao dịch
curl http://localhost:5000/api/v1/payments
```

> ⚠️ Response v1 sẽ chứa các headers:
> ```
> Deprecation: true
> Sunset: Tue, 31 Dec 2025 23:59:59 GMT
> Warning: 299 - "This API version (v1) is deprecated..."
> ```

---

#### API v2 (STABLE — Khuyến nghị dùng)

```bash
# POST — Tạo giao dịch
curl -X POST http://localhost:5000/api/v2/payments \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-001",
    "amount": 150000.0,
    "currency": "VND",
    "payment_method": "e_wallet",
    "payment_details": {
      "provider": "MoMo",
      "account": "0901234567"
    },
    "billing_address": {
      "full_name": "Nguyen Van A",
      "phone": "0901234567",
      "address": "123 Nguyen Hue",
      "city": "Ho Chi Minh"
    }
  }'

# GET — Danh sách giao dịch (có phân trang)
curl "http://localhost:5000/api/v2/payments?page=1&limit=10"
```

---

### Query Parameter Versioning (Tham khảo)

```bash
# POST — Thanh toán qua query param version=1
curl -X POST "http://localhost:5000/api/payments?version=1" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-002",
    "amount": 100000,
    "payment_method": "card",
    "card_number": "4111111111111111"
  }'

# POST — Thanh toán qua query param version=2
curl -X POST "http://localhost:5000/api/payments?version=2" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD-002",
    "amount": 100000.0,
    "currency": "VND",
    "payment_method": "bank_transfer",
    "payment_details": { "bank_code": "VCB", "account": "1234567890" },
    "billing_address": {
      "full_name": "Tran Thi B",
      "phone": "0912345678",
      "address": "456 Le Loi",
      "city": "Ha Noi"
    }
  }'

# GET — Kiểm tra thông tin endpoint
curl "http://localhost:5000/api/payments?version=2"
```

---

## Concepts Được Minh Hoạ

| Concept | Triển khai trong code |
|---|---|
| URL Versioning | `/api/v1/` và `/api/v2/` Blueprint riêng biệt |
| Query Param Versioning | `/api/payments?version=X` Blueprint |
| Deprecation Headers | `Deprecation`, `Sunset`, `Link`, `Warning` headers |
| Breaking Changes | Payload khác nhau hoàn toàn giữa v1 và v2 |
| Application Factory | `create_app()` trong `app/__init__.py` |
| Blueprint Pattern | Module hóa theo version |
| API Lifecycle | Documented trong `MIGRATION_PLAN.md` |

---

## Tài liệu liên quan

- [Kế hoạch Migration 4 Giai đoạn](./docs/MIGRATION_PLAN.md)
- [Email Thông báo Deprecation](./docs/DEPRECATION_NOTICE.md)
- [RFC 8594 — The Sunset HTTP Header](https://www.rfc-editor.org/rfc/rfc8594)
- [RFC 8288 — Web Linking (Link header)](https://www.rfc-editor.org/rfc/rfc8288)
