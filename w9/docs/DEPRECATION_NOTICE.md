# Thông Báo Ngừng Hỗ Trợ — Payment API v1

---

**Từ:** Nhóm Nền Tảng API \<api-platform@paymentservice.com\>
**Đến:** Đối Tác & Nhà Phát Triển \<developers@paymentservice.com\>
**Chủ đề:** [Yêu Cầu Hành Động] Ngừng Hỗ Trợ Payment API v1 — Vui lòng chuyển sang v2 trước ngày 31/12/2025
**Mức độ ưu tiên:** Cao

---

Kính gửi Nhà Phát Triển,

Chúng tôi viết thư này để thông báo rằng **Payment API v1** (`/api/v1/payments`) sẽ **chính thức bị khai tử vào ngày 31/12/2025**. Với tư cách là đối tác đang sử dụng API này, bạn cần thực hiện các bước cần thiết để đảm bảo dịch vụ không bị gián đoạn.

---

## Tại Sao Chúng Tôi Nâng Cấp?

Chúng tôi đã lắng nghe phản hồi của bạn và xác định một số hạn chế trong v1 cản trở việc cung cấp trải nghiệm thanh toán tốt hơn:

1. **Hạn chế phương thức thanh toán** — v1 chỉ hỗ trợ thanh toán bằng thẻ, bỏ lỡ nhu cầu ngày càng tăng về chuyển khoản ngân hàng và ví điện tử (MoMo, ZaloPay, VNPay).
2. **Xử lý số tiền không linh hoạt** — v1 sử dụng số nguyên cho trường `amount`, gây ra sai số trong một số phép tính tài chính.
3. **Thiếu thông tin địa chỉ thanh toán** — v1 không thu thập địa chỉ thanh toán, trong khi đây là yêu cầu bắt buộc theo quy định tuân thủ tài chính hiện hành (Thông tư 09/2023/TT-NHNN).
4. **Không minh bạch phí giao dịch** — v1 không trả về thông tin phí chi tiết, gây khó khăn cho việc đối soát của các đơn vị kinh doanh.

**API v2 giải quyết tất cả các vấn đề trên** đồng thời cung cấp nền tảng mạnh mẽ, có khả năng mở rộng hơn cho các tính năng thanh toán trong tương lai.

---

## Breaking Changes: Những Thay Đổi Cụ Thể

Các thay đổi sau đây **không tương thích ngược**. Bạn bắt buộc phải cập nhật mã tích hợp của mình.

### 1. Cấu Trúc Request Payload

**Request v1** *(hiện tại — sẽ ngừng hoạt động vào ngày 31/12/2025)*:
```json
{
  "order_id": "ORD-001",
  "amount": 150000,
  "payment_method": "card",
  "card_number": "4111111111111111"
}
```

**Request v2** *(mới — bắt buộc từ bây giờ)*:
```json
{
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
    "address": "123 Nguyen Hue, Quan 1",
    "city": "Ho Chi Minh"
  }
}
```

### 2. Tổng Hợp Các Trường Thay Đổi

| Trường | v1 | v2 | Mức độ ảnh hưởng |
|---|---|---|---|
| `amount` | `integer` | `float` | **Breaking** — Cập nhật kiểu dữ liệu |
| `currency` | ❌ Không có | ✅ **Bắt buộc** (`"VND"`) | **Breaking** — Phải thêm mới |
| `payment_method` | Chỉ `"card"` | `"card"`, `"bank_transfer"`, `"e_wallet"` | Non-breaking |
| `card_number` | Trường cấp cao nhất | Nằm trong object `payment_details` | **Breaking** — Phải chuyển vị trí |
| `billing_address` | ❌ Không có | ✅ Object **bắt buộc** | **Breaking** — Phải thêm mới |

### 3. Thay Đổi Response

Response của v2 bổ sung thêm các trường mới:

```json
{
  "transaction_id": "TXN-V2-20250701120000000001",
  "status": "success",
  "api_version": "v2",
  "amount": 150000.0,
  "fee": 3750.0,
  "net_amount": 146250.0,
  "currency": "VND",
  "processed_at": "2025-07-01T12:00:00Z"
}
```

> **Lưu ý**: `fee` và `net_amount` là các trường hoàn toàn mới. Nếu code của bạn phân tích response theo cách nghiêm ngặt, hãy đảm bảo nó xử lý được các trường không xác định một cách linh hoạt (chúng tôi khuyến nghị dùng parser mềm dẻo).

---

## Lịch Trình Ngừng Hỗ Trợ

| Ngày | Sự kiện |
|---|---|
| **01/07/2025** | ✅ API v2 **ra mắt chính thức** và ổn định — bắt đầu kiểm thử ngay |
| **15/07/2025** | ⚠️ v1 chính thức **bị đánh dấu Deprecated** (headers được gắn vào mọi response) |
| **01/10/2025** | 🔶 v1 bắt đầu **Brownout**: 1 giờ/tuần (02:00–03:00 UTC, thứ Tư) |
| **01/11/2025** | 🔶 Brownout leo thang: 4 giờ/tuần |
| **15/11/2025** | 🔶 Brownout leo thang: 14 giờ/tuần (hàng ngày 02:00–04:00 UTC) |
| **31/12/2025** | 🛑 v1 **bị khai tử vĩnh viễn** — trả về `HTTP 410 Gone` |

> Bắt đầu từ **15/07/2025**, mọi response của API v1 sẽ bao gồm các HTTP header sau để giúp bạn phát hiện deprecation theo cách lập trình:
> ```
> Deprecation: true
> Sunset: Tue, 31 Dec 2025 23:59:59 GMT
> Link: <https://api.paymentservice.com/api/v2/payments>; rel="successor-version"
> ```

---

## Bạn Cần Làm Gì

### Bước 1 — Đọc Hướng Dẫn Migration
Tài liệu migration đầy đủ với các ví dụ code bằng Python, Node.js, PHP và cURL có tại:
👉 **https://api.paymentservice.com/docs/migrate-v1-to-v2**

### Bước 2 — Kiểm Thử với v2 trên Môi Trường Staging
Thông tin xác thực sandbox của bạn hoạt động ngay với v2. Không cần API key mới.

Endpoint staging: `https://sandbox.paymentservice.com/api/v2/payments`

### Bước 3 — Cập Nhật Code Tích Hợp
Các thay đổi chính cần thực hiện trong code của bạn:
- Đổi URL endpoint từ `/api/v1/payments` sang `/api/v2/payments`
- Thêm trường `currency` (giá trị `"VND"`) vào request payload
- Chuyển `card_number` vào trong object `payment_details`
- Thêm object `billing_address` vào request payload
- Cập nhật `amount` sang kiểu `float`

### Bước 4 — Deploy lên Production
Sau khi kiểm thử xong, deploy tích hợp mới lên môi trường production.

**Chúng tôi khuyến nghị hoàn tất migration trước ngày 01/10/2025** (trước khi Brownout bắt đầu) để tránh gây gián đoạn cho người dùng của bạn.

### Bước 5 — Xác Nhận và Thông Báo Cho Chúng Tôi
Sau khi chuyển sang v2 trên production, vui lòng gửi email cho chúng tôi tại **api-support@paymentservice.com** để chúng tôi có thể:
- Theo dõi quá trình chuyển đổi traffic của bạn
- Cung cấp hỗ trợ bổ sung nếu cần
- Xóa bạn khỏi danh sách bị ảnh hưởng bởi Brownout

---

## Hỗ Trợ & Tài Nguyên

| Tài nguyên | Đường dẫn |
|---|---|
| Tài liệu API v2 | https://api.paymentservice.com/docs/v2 |
| Hướng dẫn Migration | https://api.paymentservice.com/docs/migrate-v1-to-v2 |
| Môi trường Sandbox | https://sandbox.paymentservice.com |
| Trang trạng thái dịch vụ | https://status.paymentservice.com |
| Hỗ trợ qua Email | api-support@paymentservice.com |
| Cộng đồng Nhà Phát Triển | https://community.paymentservice.com |

Chúng tôi cũng sẽ tổ chức **webinar Q&A trực tuyến vào ngày 20/07/2025 lúc 14:00 ICT**. Đăng ký tại: https://paymentservice.com/webinar/v2-migration

---

## Câu Hỏi Thường Gặp

**H: API key hiện tại của tôi có dùng được với v2 không?**
Đ: Có. Không cần thông tin xác thực mới.

**H: Dữ liệu giao dịch trong v1 sẽ ra sao sau khi Sunset?**
Đ: Dữ liệu giao dịch lịch sử được giữ nguyên. Chỉ có API endpoint là ngừng nhận request mới.

**H: Tôi có thể xin gia hạn sau ngày 31/12/2025 không?**
Đ: Không có gia hạn. Nghĩa vụ tuân thủ quy định yêu cầu chúng tôi phải thực thi đúng lịch trình này.

**H: Điều gì xảy ra nếu tôi gọi v1 sau ngày 31/12/2025?**
Đ: Bạn sẽ nhận được `HTTP 410 Gone` kèm thông báo lỗi. Không có giao dịch nào được xử lý.

---

Chúng tôi hiểu rằng việc migration đòi hỏi nỗ lực, và chúng tôi cam kết hỗ trợ để quá trình chuyển đổi này diễn ra thuận lợi nhất có thể. Xin đừng ngần ngại liên hệ — đội ngũ của chúng tôi luôn sẵn sàng hỗ trợ bạn.

Cảm ơn bạn đã là đối tác tin cậy của chúng tôi.

Trân trọng,

**Nhóm Nền Tảng API**
PaymentService Inc.
api-platform@paymentservice.com
https://api.paymentservice.com

---

*Bạn nhận được email này vì tài khoản của bạn đang được đăng ký là người dùng tích cực của Payment API v1. Để hủy đăng ký nhận thông báo kỹ thuật, vui lòng liên hệ api-support@paymentservice.com — lưu ý rằng các thông báo dịch vụ quan trọng không thể hủy đăng ký.*
