# Migration Plan: Payment API v1 → v2

## Tổng quan

| Thuộc tính | Chi tiết |
|---|---|
| **API hiện tại** | Payment API v1 (`/api/v1/payments`) |
| **API mới** | Payment API v2 (`/api/v2/payments`) |
| **Loại thay đổi** | Breaking Changes |
| **Ngày bắt đầu kế hoạch** | 01/07/2025 |
| **Ngày tắt hoàn toàn v1** | 31/12/2025 |

---

## Breaking Changes: v1 → v2

| Trường | v1 (Cũ) | v2 (Mới) | Loại thay đổi |
|---|---|---|---|
| `amount` | `int` (VND nguyên) | `float` (VND) | Breaking |
| `payment_method` | Chỉ `"card"` | `"card"`, `"bank_transfer"`, `"e_wallet"` | Non-breaking |
| `card_number` | Top-level field | Lồng trong `payment_details` | Breaking |
| `billing_address` | Không có | **Bắt buộc** (object) | Breaking |
| `currency` | Không có | **Bắt buộc** (string) | Breaking |
| Response `fee` | Không có | Có (float) | Non-breaking |
| Response `net_amount` | Không có | Có (float) | Non-breaking |

---

## Kế hoạch Migration 4 Giai đoạn

### Giai đoạn 1 — Release v2 (01/07/2025 – 14/07/2025)

**Mục tiêu**: Đưa v2 vào production mà không ảnh hưởng v1.

**Hành động**:
- [ ] Deploy API v2 song song với v1 (v1 vẫn hoạt động bình thường)
- [ ] Publish tài liệu v2 đầy đủ lên Developer Portal
- [ ] Mở beta access cho các đối tác sớm (early adopters)
- [ ] Viết migration guide và code samples (curl, Python, Node.js)
- [ ] Chạy load test để đảm bảo v2 đủ ổn định trước khi thông báo rộng rãi

**Tiêu chí hoàn thành**:
- v2 chạy ổn định ≥ 7 ngày liên tục, error rate < 0.1%
- Tài liệu đã được review bởi ≥ 2 technical writer

---

### Giai đoạn 2 — Deprecate v1 (15/07/2025 – 31/08/2025)

**Mục tiêu**: Thông báo chính thức v1 bị deprecated, bắt đầu khuyến khích migration.

**Hành động**:
- [ ] Gắn Deprecation Headers vào mọi response của v1:
  ```
  Deprecation: true
  Sunset: Tue, 31 Dec 2025 23:59:59 GMT
  Link: <https://api.paymentservice.com/api/v2/payments>; rel="successor-version"
  Warning: 299 - "API v1 is deprecated..."
  ```
- [ ] Gửi email thông báo chính thức đến tất cả developers (xem mục 3)
- [ ] Cập nhật Developer Portal: thêm banner "⚠️ Deprecated" lên trang v1
- [ ] Tổ chức webinar/office hours hỗ trợ migration
- [ ] Tạo dashboard theo dõi tỷ lệ traffic v1 vs v2

**Tiêu chí hoàn thành**:
- 100% developers đã nhận email thông báo (có tracking mở mail)
- Traffic v2 đạt ≥ 20% tổng traffic

---

### Giai đoạn 3 — Monitoring & Brownout (01/09/2025 – 30/11/2025)

**Mục tiêu**: Theo dõi tiến độ migration, áp lực nhẹ để thúc đẩy chuyển đổi.

**Hành động**:

**3a. Continuous Monitoring**:
- [ ] Theo dõi daily active clients trên v1 (phân loại theo API key)
- [ ] Alert tự động nếu có client "mắc kẹt" ở v1 lâu hơn 30 ngày
- [ ] Weekly report gửi nội bộ: tỷ lệ migration, error rates, top issues

**3b. Brownout Schedule** *(bắt đầu từ 01/10/2025)*:

Brownout = tạm thời tắt v1 trong các khung giờ thấp điểm, trả về `HTTP 503` với body hướng dẫn.

| Thời điểm | Lịch Brownout |
|---|---|
| 01/10/2025 | Tắt v1 mỗi thứ 4, 02:00–03:00 UTC (1 giờ/tuần) |
| 01/11/2025 | Tắt v1 thứ 2 + thứ 4, 02:00–04:00 UTC (4 giờ/tuần) |
| 15/11/2025 | Tắt v1 mỗi ngày 02:00–04:00 UTC (14 giờ/tuần) |

Response khi Brownout:
```json
{
  "error": "API v1 is temporarily unavailable (brownout period).",
  "migrate_to": "https://api.paymentservice.com/api/v2/payments",
  "docs": "https://api.paymentservice.com/docs/migrate-v1-to-v2",
  "sunset_date": "2025-12-31"
}
```

**3c. Proactive Outreach**:
- [ ] Liên hệ trực tiếp (email + Slack) với các clients vẫn dùng v1 sau 01/10/2025
- [ ] Offer 1-on-1 migration support session cho enterprise clients

**Tiêu chí hoàn thành**:
- Traffic v1 < 5% tổng traffic trước ngày 30/11/2025

---

### Giai đoạn 4 — Sunset v1 (01/12/2025 – 31/12/2025)

**Mục tiêu**: Khai tử hoàn toàn v1.

**Hành động**:
- [ ] Gửi email nhắc nhở lần cuối (D-30, D-7, D-1) cho clients còn trên v1
- [ ] 31/12/2025 23:59 UTC: Tắt v1 hoàn toàn
- [ ] v1 trả về `HTTP 410 Gone` vĩnh viễn với body hướng dẫn
- [ ] Giữ response `410` tối thiểu 6 tháng (tránh làm khách hàng bị silent fail)
- [ ] Archiver tài liệu v1 vào trang "Legacy API" (không xoá hẳn)
- [ ] Giải phóng tài nguyên server v1

Response sau Sunset:
```json
{
  "error": "API v1 has been permanently decommissioned.",
  "status": 410,
  "message": "Please use API v2 at /api/v2/payments.",
  "docs": "https://api.paymentservice.com/docs/migrate-v1-to-v2",
  "decommissioned_at": "2025-12-31T23:59:59Z"
}
```

**Tiêu chí hoàn thành**:
- 0 active requests đến v1 trong 7 ngày liên tiếp sau Sunset
- Post-mortem report được publish nội bộ

---

## Timeline Tổng hợp

```
Jul 2025       Aug 2025      Sep 2025      Oct–Nov 2025     Dec 2025
|              |             |             |                |
[  Release v2 ][  Deprecate ][  Monitor   ][ Brownout      ][ SUNSET ]
01/07  14/07  15/07  31/08  01/09  30/09  01/10    30/11  01/12  31/12
```

---

## Rollback Plan

Nếu v2 phát sinh lỗi nghiêm trọng trong giai đoạn 1:
1. Dừng gửi traffic mới đến v2
2. Thông báo với developers: v2 đang được điều tra
3. Giữ v1 hoạt động bình thường cho đến khi v2 ổn định lại
4. Không set Deprecation headers cho đến khi v2 ổn định ≥ 14 ngày liên tục

---

## RACI Matrix

| Nhiệm vụ | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Deploy v2 | Backend Team | Engineering Lead | DevOps | All Devs |
| Viết docs | API Team | Product Manager | Tech Writers | Partners |
| Gửi email | Developer Relations | VP Engineering | Legal | All Partners |
| Monitor traffic | SRE Team | Engineering Lead | Backend Team | Management |
| Thực thi Sunset | Backend Team | Engineering Lead | DevOps, Legal | All Partners |
