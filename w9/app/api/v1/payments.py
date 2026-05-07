# app/api/v1/payments.py
# -------------------------------------------------------
# Blueprint: API v1 — Payment Endpoint (DEPRECATED)
#
# Đây là phiên bản đầu tiên của Payment API.
# V1 vẫn hoạt động bình thường nhưng được đánh dấu
# DEPRECATED — sẽ bị khai tử vào ngày 31/12/2025.
#
# Breaking changes so với v2:
#   - Payload chỉ hỗ trợ 'card' payment_method
#   - Không có trường 'billing_address'
#   - amount là số nguyên (cents) thay vì float (VND)
# -------------------------------------------------------

from flask import Blueprint, request, jsonify, make_response
from datetime import datetime

# Khởi tạo Blueprint với tên 'v1' để Flask phân biệt nội bộ
v1_blueprint = Blueprint("v1", __name__)

# -------------------------------------------------------
# Ngày Sunset — ngày v1 chính thức bị tắt hoàn toàn.
# Được định nghĩa tập trung để dễ thay đổi sau này.
# Định dạng RFC 7231 (HTTP-date) theo chuẩn RFC 8594.
# -------------------------------------------------------
SUNSET_DATE = "Tue, 31 Dec 2025 23:59:59 GMT"

# -------------------------------------------------------
# URL tài liệu migration hướng dẫn khách hàng chuyển v2
# -------------------------------------------------------
MIGRATION_DOCS_URL = "https://api.paymentservice.com/docs/migrate-v1-to-v2"
V2_ENDPOINT = "https://api.paymentservice.com/api/v2/payments"


def _add_deprecation_headers(response):
    """
    Helper: Gắn các HTTP Headers chuẩn để báo hiệu API bị deprecated.

    - Deprecation: true           — RFC 8594; báo endpoint này sẽ bị loại bỏ.
    - Sunset: <date>              — RFC 8594; thông báo ngày chính thức tắt.
    - Link: <url>; rel="successor-version" — chỉ đường tới v2.
    - Warning: 299                — HTTP/1.1 Generic Warning cho các client cũ.
    """
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = SUNSET_DATE
    response.headers["Link"] = (
        f'<{V2_ENDPOINT}>; rel="successor-version", '
        f'<{MIGRATION_DOCS_URL}>; rel="deprecation"'
    )
    response.headers["Warning"] = (
        '299 - "This API version (v1) is deprecated and will be '
        f'removed on {SUNSET_DATE}. Please migrate to /api/v2/payments."'
    )
    return response


@v1_blueprint.route("/payments", methods=["POST"])
def create_payment_v1():
    """
    POST /api/v1/payments
    ---------------------
    Xử lý thanh toán theo logic v1 (cũ).

    Expected Request Body (JSON):
    {
        "order_id":       "ORD-001",      # ID đơn hàng
        "amount":         150000,          # Số tiền (đơn vị: VND nguyên)
        "payment_method": "card",          # Chỉ hỗ trợ "card"
        "card_number":    "4111111111111111"
    }

    Response (JSON):
    {
        "transaction_id": "...",
        "status":         "success",
        "amount_paid":    150000,
        "message":        "..."
    }
    """
    data = request.get_json()

    # --- Validation cơ bản ---
    required_fields = ["order_id", "amount", "payment_method", "card_number"]
    for field in required_fields:
        if field not in data:
            resp = make_response(
                jsonify({"error": f"Missing required field: '{field}'"}), 400
            )
            return _add_deprecation_headers(resp)

    # --- V1 chỉ hỗ trợ phương thức 'card' ---
    if data["payment_method"] != "card":
        resp = make_response(
            jsonify({
                "error": "v1 only supports 'card' payment method. "
                         "Use v2 for more options."
            }),
            422,
        )
        return _add_deprecation_headers(resp)

    # --- Mô phỏng xử lý thanh toán ---
    transaction_id = f"TXN-V1-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    payload = {
        "transaction_id": transaction_id,
        "status":         "success",
        "api_version":    "v1",
        "amount_paid":    data["amount"],      # Trả về nguyên giá trị VND (int)
        "order_id":       data["order_id"],
        "message":        (
            "Payment processed successfully via API v1. "
            "NOTE: This API is DEPRECATED — please migrate to v2."
        ),
    }

    resp = make_response(jsonify(payload), 200)
    # Gắn deprecation headers vào mọi response của v1
    return _add_deprecation_headers(resp)


@v1_blueprint.route("/payments", methods=["GET"])
def list_payments_v1():
    """
    GET /api/v1/payments
    --------------------
    Trả về danh sách giao dịch (mock data) cho v1.
    Mục đích minh hoạ: v1 không có phân trang nâng cao.
    """
    mock_transactions = [
        {"transaction_id": "TXN-V1-001", "amount": 100000, "status": "success"},
        {"transaction_id": "TXN-V1-002", "amount": 200000, "status": "failed"},
    ]

    resp = make_response(jsonify({
        "api_version":   "v1",
        "transactions":  mock_transactions,
        "total":         len(mock_transactions),
    }), 200)

    return _add_deprecation_headers(resp)
