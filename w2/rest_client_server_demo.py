"""
MINH HỌA NGUYÊN TẮC CLIENT–SERVER CỦA KIẾN TRÚC REST
=====================================================

Ý tưởng chính:
- **Client** (Frontend / Mobile App / Postman / Browser) chỉ quan tâm tới tài nguyên và API.
- **Server** (REST API) chịu trách nhiệm lưu trữ dữ liệu, xử lý nghiệp vụ, bảo mật.
- Hai bên giao tiếp thông qua **HTTP request/response**, độc lập về triển khai.

File này tập trung minh họa phía **SERVER** (REST API) bằng Flask.
Bạn có thể dùng bất kỳ client nào (curl/Postman/browser/JS frontend) để gọi.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)


# "CSDL" giả lập lưu trên server
USERS = {
    1: {"id": 1, "name": "Alice", "role": "student"},
    2: {"id": 2, "name": "Bob", "role": "teacher"},
}


@app.route("/api/client-server/info", methods=["GET"])
def client_server_info():
    """
    Endpoint giải thích bằng JSON về nguyên tắc client–server trong REST.
    """
    return jsonify(
        {
            "principle": "client-server",
            "description": (
                "Client và Server tách biệt. Client chỉ biết tới URI/API và representation "
                "(JSON/XML...). Server chịu trách nhiệm xử lý nghiệp vụ và lưu trữ dữ liệu."
            ),
            "benefits": [
                "Client và server có thể phát triển, deploy độc lập.",
                "Có thể thay đổi giao diện client mà không ảnh hưởng đến server.",
                "Có thể scale server mà không ảnh hưởng đến client, và ngược lại.",
            ],
            "example_endpoints": [
                "/api/client-server/users",
                "/api/client-server/users/<id>",
            ],
        }
    )


@app.route("/api/client-server/users", methods=["GET"])
def list_users():
    """
    GET /api/client-server/users

    Minh họa:
    - Client chỉ cần gọi đúng URI này.
    - Không cần biết server dùng Flask, Python, database gì.
    """
    return jsonify(
        {
            "count": len(USERS),
            "users": list(USERS.values()),
        }
    )


@app.route("/api/client-server/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """
    GET /api/client-server/users/<id>

    - Client gửi request với id.
    - Server tìm trong "CSDL" và trả kết quả.
    - Format response (JSON) là hợp đồng chung giữa client và server.
    """
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/api/client-server/users", methods=["POST"])
def create_user():
    """
    POST /api/client-server/users

    - Client gửi JSON body lên server.
    - Server xử lý, lưu dữ liệu và trả lại representation của resource vừa tạo.

    Ví dụ body client gửi:
    {
        "name": "Charlie",
        "role": "student"
    }
    """
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    new_id = max(USERS.keys(), default=0) + 1
    user = {"id": new_id, "name": name, "role": data.get("role", "student")}
    USERS[new_id] = user
    return jsonify(user), 201


"""
GỢI Ý CÁCH TEST ĐỂ THẤY RÕ CLIENT–SERVER
========================================

1. Chạy server (phía SERVER – REST API):
   python rest_client_server_demo.py

2. Từ phía CLIENT (ví dụ dùng curl hoặc Postman):

   - Lấy thông tin nguyên tắc client-server:
     curl http://localhost:5002/api/client-server/info

   - Lấy danh sách users:
     curl http://localhost:5002/api/client-server/users

   - Lấy 1 user cụ thể:
     curl http://localhost:5002/api/client-server/users/1

   - Tạo user mới:
     curl -X POST http://localhost:5002/api/client-server/users ^
          -H "Content-Type: application/json" ^
          -d "{\"name\": \"Charlie\", \"role\": \"student\"}"

Quan sát:
- Code trong file này chỉ là SERVER.
- Client có thể là: Postman, web app React, Android, iOS, ứng dụng desktop...
- Thay đổi client không cần sửa code server (miễn là giữ nguyên API contract).
"""


if __name__ == "__main__":
    # Dùng port 5002 để không trùng với các demo khác.
    app.run(debug=True, port=5002)

