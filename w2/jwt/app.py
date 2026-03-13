"""
Flask REST API với JWT thực tế: DB SQLite, hash mật khẩu, phân quyền từ DB.

- Login: xác thực user từ DB, so sánh password hash, cấp JWT (encode).
- Me / Verify: decode JWT, role trong token lấy từ DB lúc login.
- RBAC: admin quản lý user/role trong DB; teacher xem khóa học từ DB; student xem điểm từ DB.
"""
from flask import Flask, jsonify, request

from config import JWT_ACCESS_TOKEN_EXPIRE_SECONDS, VALID_ROLES
from jwt_utils import encode_token, decode_token
from auth import get_current_user, get_token_from_request, require_roles, require_min_role
import database as db

app = Flask(__name__)

API_PREFIX = "/api/v1"

# Khởi tạo DB khi chạy app (tạo bảng + seed nếu trống)
db.init_db()


# ---------- Public ----------

@app.route(f"{API_PREFIX}/health", methods=["GET"])
def health():
    """GET /api/v1/health — Kiểm tra server, không cần token."""
    return jsonify({"status": "ok", "service": "jwt-rest-api"}), 200


@app.route(f"{API_PREFIX}/auth/login", methods=["POST"])
def login():
    """
    POST /api/v1/auth/login

    Body: { "username": "...", "password": "..." }
    Xác thực từ DB (hash mật khẩu), trả về JWT.
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return (
            jsonify({
                "error": "Bad Request",
                "message": "Cần gửi username và password trong body JSON.",
            }),
            400,
        )

    user = db.get_user_by_username(username)
    if not user or not db.verify_password(user, password):
        return (
            jsonify({
                "error": "Unauthorized",
                "message": "Sai tên đăng nhập hoặc mật khẩu.",
            }),
            401,
        )

    # JWT standard: "sub" (subject) nên là string; PyJWT có thể reject nếu sub là int
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
    }
    access_token = encode_token(payload)
    # print(decode_token(access_token))
    return (
        jsonify({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
            },
        }),
        201,
    )


@app.route(f"{API_PREFIX}/auth/verify", methods=["GET"])
def verify():
    """GET /api/v1/auth/verify — Xác thực token (decode), trả về payload nếu hợp lệ."""
    token = get_token_from_request()
    if not token:
        return (
            jsonify({
                "error": "Unauthorized",
                "message": "Thiếu header Authorization: Bearer <token>",
            }),
            401,
        )
    payload = decode_token(token)
    if not payload:
        return (
            jsonify({
                "error": "Unauthorized",
                "message": "Token không hợp lệ hoặc đã hết hạn.",
            }),
            401,
        )
    return jsonify({
        "valid": True,
        "payload": {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
        },
    }), 200


# ---------- Protected: cần token ----------

@app.route(f"{API_PREFIX}/auth/me", methods=["GET"])
def me():
    """
    GET /api/v1/auth/me

    Thông tin user từ JWT. Có thể bổ sung dữ liệu mới nhất từ DB (optional).
    """
    user = get_current_user()
    if not user:
        return (
            jsonify({
                "error": "Unauthorized",
                "message": "Gửi header Authorization: Bearer <token> với token hợp lệ.",
            }),
            401,
        )
    # Có thể lấy thêm từ DB để đảm bảo role mới nhất (sau khi admin đổi role)
    uid = user.get("sub")
    if isinstance(uid, str) and uid.isdigit():
        uid = int(uid)
    db_user = db.get_user_by_id(uid) if isinstance(uid, int) else None
    if db_user:
        return jsonify({
            "user_id": db_user["id"],
            "username": db_user["username"],
            "role": db_user["role"],
            "created_at": db_user["created_at"],
        }), 200
    return jsonify({
        "user_id": user.get("sub"),
        "username": user.get("username"),
        "role": user.get("role"),
    }), 200


# ---------- RBAC: Admin — quản lý user thực từ DB ----------

@app.route(f"{API_PREFIX}/admin/dashboard", methods=["GET"])
@require_roles("admin")
def admin_dashboard():
    """GET /api/v1/admin/dashboard — Thống kê thực từ DB."""
    total = db.count_users()
    return jsonify({
        "message": "Khu vực quản trị. Số liệu từ database.",
        "stats": {
            "total_users": total,
            "roles": list(VALID_ROLES),
        },
    }), 200


@app.route(f"{API_PREFIX}/admin/users", methods=["GET"])
@require_roles("admin")
def admin_list_users():
    """GET /api/v1/admin/users — Danh sách user từ DB (chỉ admin)."""
    users = db.list_users()
    return jsonify({
        "items": users,
        "total": len(users),
    }), 200


@app.route(f"{API_PREFIX}/admin/users", methods=["POST"])
@require_roles("admin")
def admin_create_user():
    """
    POST /api/v1/admin/users

    Body: { "username": "...", "password": "...", "role": "student" }
    Tạo user mới trong DB (password được hash).
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "student").strip().lower()

    if not username or not password:
        return (
            jsonify({
                "error": "Bad Request",
                "message": "Cần username và password.",
            }),
            400,
        )
    if role not in VALID_ROLES:
        return (
            jsonify({
                "error": "Bad Request",
                "message": f"role phải là một trong: {sorted(VALID_ROLES)}",
            }),
            400,
        )
    new_user = db.create_user(username, password, role)
    if not new_user:
        return (
            jsonify({
                "error": "Conflict",
                "message": "Username đã tồn tại.",
            }),
            409,
        )
    return jsonify(new_user), 201


@app.route(f"{API_PREFIX}/admin/users/<int:user_id>/role", methods=["PUT"])
@require_roles("admin")
def admin_update_user_role(user_id: int):
    """
    PUT /api/v1/admin/users/<id>/role

    Body: { "role": "teacher" }
    Đổi role của user trong DB (phân quyền thực tế).
    """
    data = request.get_json(silent=True) or {}
    role = (data.get("role") or "").strip().lower()
    if not role or role not in VALID_ROLES:
        return (
            jsonify({
                "error": "Bad Request",
                "message": f"Body cần 'role' là một trong: {sorted(VALID_ROLES)}",
            }),
            400,
        )
    if not db.get_user_by_id(user_id):
        return jsonify({"error": "Not Found", "message": "User không tồn tại."}), 404
    ok = db.update_user_role(user_id, role)
    if not ok:
        return jsonify({"error": "Bad Request", "message": "Không thể cập nhật role."}), 400
    updated = db.get_user_by_id(user_id)
    return jsonify(updated), 200


# ---------- RBAC: Teacher — khóa học thực từ DB ----------

@app.route(f"{API_PREFIX}/teachers/courses", methods=["GET"])
@require_min_role("teacher")
def teachers_courses():
    """
    GET /api/v1/teachers/courses

    Danh sách khóa học từ DB: admin xem hết, teacher chỉ xem khóa của mình.
    """
    user = request.current_user
    uid = user.get("sub")
    if isinstance(uid, str) and uid.isdigit():
        uid = int(uid)
    if user.get("role") == "admin":
        teacher_id = None
    else:
        teacher_id = uid if isinstance(uid, int) else None
    items = db.list_courses_for_api(teacher_id=teacher_id)
    return jsonify({
        "message": "Danh sách khóa học từ database.",
        "items": items,
    }), 200


# ---------- RBAC: Student — điểm thực từ DB ----------

@app.route(f"{API_PREFIX}/students/grades", methods=["GET"])
@require_roles("student", "teacher", "admin")
def students_grades():
    """
    GET /api/v1/students/grades

    Điểm của user hiện tại từ DB. Student xem của mình; teacher/admin có thể mở rộng sau (query param ?student_id=).
    """
    user = request.current_user
    uid = user.get("sub")
    if isinstance(uid, str) and uid.isdigit():
        uid = int(uid)
    if not isinstance(uid, int):
        return jsonify({"error": "Bad Request", "message": "Token không hợp lệ."}), 400
    # Hiện tại: mỗi user xem điểm của chính mình (student_id = uid)
    grades = db.list_grades_by_student(uid)
    return jsonify({
        "message": f"Điểm của user {user.get('username')} (từ database).",
        "grades": grades,
    }), 200


# ---------- Public info ----------

@app.route(f"{API_PREFIX}/info", methods=["GET"])
def info():
    """GET /api/v1/info — Mô tả API, JWT và RBAC thực tế."""
    return jsonify({
        "api": "JWT REST API (real data)",
        "version": "v1",
        "principle": "stateless",
        "auth": "Password hash (werkzeug), role từ database. JWT chứa sub, username, role.",
        "endpoints": {
            "POST /api/v1/auth/login": "Đăng nhập (DB + hash), trả về JWT.",
            "GET /api/v1/auth/me": "Thông tin user (có thể sync từ DB).",
            "GET /api/v1/auth/verify": "Kiểm tra token.",
            "GET /api/v1/admin/dashboard": "RBAC admin — thống kê từ DB.",
            "GET /api/v1/admin/users": "RBAC admin — danh sách user từ DB.",
            "POST /api/v1/admin/users": "RBAC admin — tạo user (hash password).",
            "PUT /api/v1/admin/users/<id>/role": "RBAC admin — đổi role user.",
            "GET /api/v1/teachers/courses": "RBAC teacher+ — khóa học từ DB.",
            "GET /api/v1/students/grades": "RBAC student+ — điểm từ DB.",
        },
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5004)
