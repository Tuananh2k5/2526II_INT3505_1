"""
MINH HỌA NGUYÊN TẮC STATELESS CỦA KIẾN TRÚC REST
=================================================

Ý tưởng chính:
- Mỗi request từ client tới server phải **tự chứa đủ thông tin** để server hiểu và xử lý.
- Server **không lưu session state của client giữa các request** (không nhớ "đã login lần trước"
  nếu không có token kèm theo, không nhớ bước trước của workflow).
- Trạng thái phiên làm việc (session) được giữ ở **client** (ví dụ: token, thông tin user),
  server chỉ dựa vào dữ liệu trong từng request để xử lý.

File này minh họa:
- Client gửi kèm "Authorization" token trong mỗi request.
- Server MỖI LẦN đều kiểm tra token, không dựa vào session lưu trên server.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)


# "Kho" token hợp lệ giả lập trên server
VALID_TOKENS = {
    "token-student-123": {"user_id": 1, "name": "Alice", "role": "student"},
    "token-teacher-456": {"user_id": 2, "name": "Bob", "role": "teacher"},
}


@app.route("/api/stateless/info", methods=["GET"])
def stateless_info():
    """
    GET /api/stateless/info

    Trả về mô tả ngắn gọn về nguyên tắc stateless.
    """
    return jsonify(
        {
            "principle": "stateless",
            "description": (
                "Mỗi request phải tự chứa đủ thông tin để server xử lý. "
                "Server không lưu session state của client giữa các request."
            ),
            "implications": [
                "Client phải gửi thông tin xác thực (token) trong MỖI request.",
                "Server xử lý request độc lập, dễ scale ngang (nhiều instance).",
                "Không phụ thuộc vào memory session trên một node cụ thể.",
            ],
            "example_protected_endpoint": "/api/stateless/profile",
        }
    )


def _get_current_user_from_token():
    """
    Lấy user từ header Authorization.

    Ví dụ client gửi:
        Authorization: Bearer token-student-123

    Nếu token hợp lệ -> trả về thông tin user.
    Nếu không -> trả về None.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ").strip()
    return VALID_TOKENS.get(token)


@app.route("/api/stateless/profile", methods=["GET"])
def stateless_profile():
    """
    GET /api/stateless/profile

    Minh họa stateless:
    - Server KHÔNG nhớ "ai đang login" giữa các request.
    - Mỗi request phải gửi kèm token trong header Authorization.
    - Server đọc token, tra trong VALID_TOKENS và quyết định trả dữ liệu nào.
    """
    user = _get_current_user_from_token()
    if not user:
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": (
                        "Request phải gửi header 'Authorization: Bearer <token>' "
                        "và token phải hợp lệ."
                    ),
                }
            ),
            401,
        )

    # Ở đây, dù là request thứ N, server vẫn dựa HOÀN TOÀN vào token trong request hiện tại.
    # Không có session lưu trong memory server cho từng client.
    return jsonify(
        {
            "message": "Thông tin profile được trả về hoàn toàn dựa trên token trong request hiện tại.",
            "user": user,
        }
    )


"""
GỢI Ý CÁCH TEST ĐỂ THẤY RÕ STATELESS
====================================

1. Chạy server:
   python rest_stateless_demo.py

2. Gọi endpoint info (không cần token):
   curl http://localhost:5003/api/stateless/info

3. Thử gọi profile KHÔNG gửi token (sẽ bị 401):
   curl http://localhost:5003/api/stateless/profile

4. Thử gọi profile VỚI token hợp lệ:
   curl http://localhost:5003/api/stateless/profile ^
        -H "Authorization: Bearer token-student-123"

5. Thử gọi lại nhiều lần với token khác nhau:
   - Lần 1 gửi token-student-123 -> nhận profile Alice.
   - Lần 2 gửi token-teacher-456 -> nhận profile Bob.

Quan sát:
- Server không "nhớ" lần trước bạn là ai, mỗi request đều phải kèm token.
- Đây là ví dụ điển hình của nguyên tắc stateless trong REST.
"""


if __name__ == "__main__":
    # Dùng port 5003 để không trùng với các demo khác.
    app.run(debug=True, port=5003)

