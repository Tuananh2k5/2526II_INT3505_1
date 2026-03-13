"""
Xác thực và phân quyền (RBAC) cho REST API.

- Lấy token từ header Authorization: Bearer <token>.
- Decode token để lấy current user (stateless).
- Decorator require_roles(...) để bảo vệ endpoint theo role.
"""
from functools import wraps
from typing import Callable, Optional

from flask import request, jsonify

from config import ROLES, VALID_ROLES
from jwt_utils import decode_token


def get_token_from_request() -> Optional[str]:
    """
    Lấy JWT từ header Authorization.

    Chuẩn REST/OAuth2: Authorization: Bearer <access_token>

    Returns:
        Chuỗi token hoặc None nếu không có / sai format.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.removeprefix("Bearer ").strip()


def get_current_user() -> Optional[dict]:
    """
    Lấy thông tin user hiện tại từ JWT trong request (stateless).

    Returns:
        Payload đã decode (có sub, role, ...) hoặc None nếu chưa đăng nhập / token invalid.
    """
    token = get_token_from_request()
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    return payload


def require_roles(*allowed_roles: str) -> Callable:
    """
    Decorator RBAC: chỉ cho phép các role được liệt kê gọi endpoint.

    Cách dùng:
        @app.route("/api/v1/admin/users")
        @require_roles("admin")
        def list_users():
            ...

    Trả về 401 nếu không có token / token invalid.
    Trả về 403 nếu có token nhưng role không đủ quyền.
    """
    allowed = set(allowed_roles)
    invalid = allowed - VALID_ROLES
    if invalid:
        raise ValueError(f"Invalid role(s) in require_roles: {invalid}")

    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return (
                    jsonify({
                        "error": "Unauthorized",
                        "message": "Token không hợp lệ hoặc thiếu. Gửi header: Authorization: Bearer <token>",
                    }),
                    401,
                )
            role = user.get("role")
            if role not in allowed:
                return (
                    jsonify({
                        "error": "Forbidden",
                        "message": f"Role '{role}' không có quyền truy cập. Yêu cầu một trong: {sorted(allowed)}",
                    }),
                    403,
                )
            # Đưa user vào request context để view dùng
            request.current_user = user
            return f(*args, **kwargs)
        return wrapped
    return decorator


def require_min_role(min_role: str) -> Callable:
    """
    Decorator RBAC: yêu cầu role có level >= min_role (theo thứ tự trong config.ROLES).

    Ví dụ: require_min_role("teacher") cho phép teacher và admin.
    """
    if min_role not in VALID_ROLES:
        raise ValueError(f"Invalid min_role: {min_role}")
    min_level = ROLES[min_role]

    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return (
                    jsonify({
                        "error": "Unauthorized",
                        "message": "Token không hợp lệ hoặc thiếu.",
                    }),
                    401,
                )
            role = user.get("role")
            role_level = ROLES.get(role, -1)
            if role_level < min_level:
                return (
                    jsonify({
                        "error": "Forbidden",
                        "message": f"Yêu cầu role tối thiểu: {min_role}. Hiện tại: {role}",
                    }),
                    403,
                )
            request.current_user = user
            return f(*args, **kwargs)
        return wrapped
    return decorator
