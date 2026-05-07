# app/api/v2/payments.py
# -------------------------------------------------------
# Blueprint: API v2 — Payment Endpoint (CURRENT / STABLE)
#
# V2 là phiên bản hiện hành, có các BREAKING CHANGES so với v1:
#
# Breaking Changes:
#   1. 'amount' giờ là số thực (float), đơn vị VND (không phải cents)
#      và bắt buộc phải > 0.
#   2. 'payment_method' mở rộng hỗ trợ: "card", "bank_transfer", "e_wallet"
#   3. Thêm object 'billing_address' BẮT BUỘC chứa các trường:
#         - full_name, phone, address, city
#   4. 'card_number' không còn là trường top-level;
#      thay vào đó dùng object 'payment_details' lồng bên trong.
#   5. Response có thêm trường 'fee', 'net_amount', 'currency'.
# -------------------------------------------------------

from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

# Khởi tạo Blueprint với tên 'v2'
v2_blueprint = Blueprint("v2", __name__)

# -------------------------------------------------------
# Phí xử lý theo từng phương thức thanh toán (% của amount)
# -------------------------------------------------------
FEE_RATES = {
    "card":          0.025,   # 2.5%
    "bank_transfer": 0.01,    # 1.0%
    "e_wallet":      0.015,   # 1.5%
}

# Các phương thức thanh toán hợp lệ ở v2
VALID_PAYMENT_METHODS = set(FEE_RATES.keys())


def _validate_billing_address(billing_address: dict) -> list[str]:
    """
    Kiểm tra object billing_address có đầy đủ trường bắt buộc không.
    Trả về list các lỗi (rỗng nếu hợp lệ).
    """
    required = ["full_name", "phone", "address", "city"]
    return [f"billing_address.{f}" for f in required if f not in billing_address]


@v2_blueprint.route("/payments", methods=["POST"])
def create_payment_v2():
    """
    POST /api/v2/payments
    ---------------------
    Xử lý thanh toán theo logic v2 (mới nhất).

    Expected Request Body (JSON) — BREAKING CHANGE so với v1:
    {
        "order_id":       "ORD-001",
        "amount":         150000.0,              # float, đơn vị VND
        "currency":       "VND",                 # THÊM MỚI: mã tiền tệ
        "payment_method": "e_wallet",            # Mở rộng: card|bank_transfer|e_wallet
        "payment_details": {                     # THÊM MỚI: nested object
            "provider": "MoMo",                  # Ví dụ cho e_wallet
            "account":  "0901234567"
        },
        "billing_address": {                     # BẮT BUỘC THÊM MỚI
            "full_name": "Nguyen Van A",
            "phone":     "0901234567",
            "address":   "123 Nguyen Hue",
            "city":      "Ho Chi Minh"
        },
        "metadata": {                            # Tuỳ chọn: dữ liệu bổ sung
            "note": "Birthday gift"
        }
    }

    Response (JSON):
    {
        "transaction_id": "...",
        "status":         "success",
        "api_version":    "v2",
        "currency":       "VND",
        "amount":         150000.0,
        "fee":            2250.0,
        "net_amount":     147750.0,
        "order_id":       "...",
        "billing_address": { ... },
        "processed_at":   "..."
    }
    """
    data = request.get_json()

    errors = []

    # --- Kiểm tra các trường bắt buộc ở top-level ---
    top_level_required = ["order_id", "amount", "currency", "payment_method", "billing_address"]
    for field in top_level_required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    # --- Kiểm tra amount hợp lệ ---
    if "amount" in data:
        try:
            amount = float(data["amount"])
            if amount <= 0:
                errors.append("'amount' must be a positive number")
        except (TypeError, ValueError):
            errors.append("'amount' must be a numeric value")
            amount = 0.0
    else:
        amount = 0.0

    # --- Kiểm tra payment_method hợp lệ ---
    if "payment_method" in data:
        if data["payment_method"] not in VALID_PAYMENT_METHODS:
            errors.append(
                f"'payment_method' must be one of: {list(VALID_PAYMENT_METHODS)}"
            )

    # --- Kiểm tra billing_address đầy đủ ---
    if "billing_address" in data:
        address_errors = _validate_billing_address(data["billing_address"])
        errors.extend([f"Missing required field: '{e}'" for e in address_errors])

    # --- Trả lỗi nếu validation thất bại ---
    if errors:
        return jsonify({"errors": errors}), 400

    # --- Tính phí giao dịch ---
    fee_rate  = FEE_RATES[data["payment_method"]]
    fee       = round(amount * fee_rate, 2)
    net_amount = round(amount - fee, 2)

    # --- Mô phỏng xử lý thanh toán thành công ---
    transaction_id = f"TXN-V2-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    return jsonify({
        "transaction_id":  transaction_id,
        "status":          "success",
        "api_version":     "v2",
        "currency":        data.get("currency", "VND"),
        "amount":          amount,
        "fee":             fee,
        "net_amount":      net_amount,
        "order_id":        data["order_id"],
        "payment_method":  data["payment_method"],
        "billing_address": data["billing_address"],
        "payment_details": data.get("payment_details", {}),
        "metadata":        data.get("metadata", {}),
        "processed_at":    datetime.utcnow().isoformat() + "Z",
        "message":         "Payment processed successfully via API v2.",
    }), 200


@v2_blueprint.route("/payments", methods=["GET"])
def list_payments_v2():
    """
    GET /api/v2/payments
    --------------------
    Trả về danh sách giao dịch (mock data) cho v2.
    V2 có hỗ trợ phân trang cơ bản qua query params: ?page=1&limit=10
    """
    # Đọc query params phân trang (mặc định page=1, limit=10)
    page  = request.args.get("page",  default=1,  type=int)
    limit = request.args.get("limit", default=10, type=int)

    mock_transactions = [
        {
            "transaction_id": "TXN-V2-001",
            "amount":         150000.0,
            "fee":            3750.0,
            "net_amount":     146250.0,
            "currency":       "VND",
            "payment_method": "card",
            "status":         "success",
        },
        {
            "transaction_id": "TXN-V2-002",
            "amount":         500000.0,
            "fee":            5000.0,
            "net_amount":     495000.0,
            "currency":       "VND",
            "payment_method": "bank_transfer",
            "status":         "success",
        },
        {
            "transaction_id": "TXN-V2-003",
            "amount":         200000.0,
            "fee":            3000.0,
            "net_amount":     197000.0,
            "currency":       "VND",
            "payment_method": "e_wallet",
            "status":         "pending",
        },
    ]

    return jsonify({
        "api_version":  "v2",
        "page":         page,
        "limit":        limit,
        "total":        len(mock_transactions),
        "transactions": mock_transactions,
    }), 200
