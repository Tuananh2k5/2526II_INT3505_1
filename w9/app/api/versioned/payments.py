# app/api/versioned/payments.py
# -------------------------------------------------------
# Blueprint: Query Parameter Versioning (Tham khảo)
#
# Đây là ví dụ minh hoạ cách triển khai API Versioning
# thông qua Query Parameter thay vì URL Path.
#
# Ưu điểm: URL sạch hơn (/api/payments thay vì /api/v1/payments)
# Nhược điểm:
#   - Khó cache hơn (CDN thường cache theo URL path)
#   - Dễ quên truyền param => gây nhầm lẫn version mặc định
#   - Ít RESTful hơn so với URL versioning
#
# Cách dùng:
#   GET/POST /api/payments?version=1    => logic v1
#   GET/POST /api/payments?version=2    => logic v2
#   GET/POST /api/payments              => mặc định về version mới nhất (v2)
# -------------------------------------------------------

from flask import Blueprint, request, jsonify

# Khởi tạo Blueprint với tên 'versioned'
versioned_blueprint = Blueprint("versioned", __name__)

# -------------------------------------------------------
# Version mặc định khi không truyền query param
# Best practice: luôn default về version ổn định mới nhất
# -------------------------------------------------------
DEFAULT_VERSION = "2"

# -------------------------------------------------------
# Các version hợp lệ hiện tại
# -------------------------------------------------------
SUPPORTED_VERSIONS = {"1", "2"}


def _handle_v1_logic(data: dict) -> tuple:
    """
    Đóng gói logic xử lý thanh toán v1.
    Tách biệt thành function riêng để dễ maintain.
    """
    required = ["order_id", "amount", "payment_method", "card_number"]
    for field in required:
        if field not in data:
            return {"error": f"Missing required field: '{field}'"}, 400

    if data["payment_method"] != "card":
        return {"error": "v1 only supports 'card' payment method."}, 422

    return {
        "api_version":    "v1 (via query param)",
        "status":         "success",
        "order_id":       data["order_id"],
        "amount_paid":    data["amount"],
        "deprecation_warning": (
            "You are using API v1 which is deprecated. "
            "Pass ?version=2 or migrate to /api/v2/payments."
        ),
    }, 200


def _handle_v2_logic(data: dict) -> tuple:
    """
    Đóng gói logic xử lý thanh toán v2.
    """
    required = ["order_id", "amount", "currency", "payment_method", "billing_address"]
    for field in required:
        if field not in data:
            return {"error": f"Missing required field: '{field}'"}, 400

    amount    = float(data["amount"])
    fee       = round(amount * 0.02, 2)   # Phí phẳng 2% để đơn giản hoá ví dụ
    net_amount = round(amount - fee, 2)

    return {
        "api_version": "v2 (via query param)",
        "status":      "success",
        "order_id":    data["order_id"],
        "currency":    data["currency"],
        "amount":      amount,
        "fee":         fee,
        "net_amount":  net_amount,
    }, 200


@versioned_blueprint.route("/payments", methods=["POST"])
def payments_query_versioned():
    """
    POST /api/payments?version=<1|2>
    --------------------------------
    Một endpoint duy nhất xử lý nhiều version thông qua
    query parameter 'version'.

    Flow:
    1. Đọc ?version=X từ query string
    2. Validate version có được hỗ trợ không
    3. Dispatch sang handler tương ứng
    """
    # Bước 1: Đọc query param 'version', fallback về DEFAULT_VERSION
    version = request.args.get("version", default=DEFAULT_VERSION, type=str)

    # Bước 2: Kiểm tra version hợp lệ
    if version not in SUPPORTED_VERSIONS:
        return jsonify({
            "error": f"Unsupported API version: '{version}'.",
            "supported_versions": list(SUPPORTED_VERSIONS),
            "hint": "Use ?version=1 or ?version=2",
        }), 400

    # Lấy request body
    data = request.get_json() or {}

    # Bước 3: Dispatch logic theo version
    if version == "1":
        result, status_code = _handle_v1_logic(data)
    else:
        result, status_code = _handle_v2_logic(data)

    response = jsonify(result)

    # -------------------------------------------------------
    # Thêm header Content-Version để client biết đang dùng version nào.
    # Đây là cách tốt dù dùng query param versioning.
    # -------------------------------------------------------
    response.headers["Content-Version"] = version
    response.headers["X-API-Version"]   = version

    return response, status_code


@versioned_blueprint.route("/payments", methods=["GET"])
def get_payments_query_versioned():
    """
    GET /api/payments?version=<1|2>
    --------------------------------
    Trả về thông tin endpoint và version đang sử dụng.
    Hữu ích để client kiểm tra version nào đang active.
    """
    version = request.args.get("version", default=DEFAULT_VERSION, type=str)

    if version not in SUPPORTED_VERSIONS:
        return jsonify({
            "error": f"Unsupported API version: '{version}'.",
            "supported_versions": list(SUPPORTED_VERSIONS),
        }), 400

    return jsonify({
        "endpoint":           "/api/payments",
        "versioning_strategy": "query_parameter",
        "active_version":     version,
        "supported_versions": list(SUPPORTED_VERSIONS),
        "default_version":    DEFAULT_VERSION,
        "note": (
            "Query parameter versioning is provided for reference only. "
            "The recommended approach is URL versioning: /api/v1/ or /api/v2/"
        ),
    }), 200
