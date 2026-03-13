"""
Tiện ích JWT: encode (tạo token), decode (xác thực và lấy payload).

Nguyên tắc REST stateless: token chứa đủ thông tin (user_id, role, exp, ...),
server không lưu session; mỗi request gửi kèm token trong header Authorization.
"""
import time
from typing import Any, Optional

import jwt

from config import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
)


def encode_token(
    payload: dict[str, Any],
    expires_delta_seconds: Optional[int] = None,
) -> str:
    """
    Tạo JWT từ payload.

    Args:
        payload: dữ liệu cần gói vào token (ví dụ: user_id, username, role).
        expires_delta_seconds: thời hạn token (giây). Mặc định dùng config.

    Returns:
        Chuỗi JWT (access token).

    Ví dụ payload:
        {"sub": "user_123", "username": "alice", "role": "student"}
    """
    now = int(time.time())
    expire = now + (expires_delta_seconds or JWT_ACCESS_TOKEN_EXPIRE_SECONDS)
    # Chuẩn JWT: "sub" = subject (thường là user id), "exp" = expiration
    full_payload = {
        **payload,
        "iat": now,   # issued at
        "exp": expire,
    }
    return jwt.encode(
        full_payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Giải mã và xác thực JWT.

    Args:
        token: chuỗi JWT (thường lấy từ header Authorization: Bearer <token>).

    Returns:
        Payload (dict) nếu token hợp lệ và chưa hết hạn;
        None nếu token sai, hết hạn hoặc bị sửa.
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("expired")
        return None
    except jwt.InvalidTokenError:
        print("invalid")
        return None
