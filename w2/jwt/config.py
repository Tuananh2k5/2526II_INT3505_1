"""
Cấu hình JWT cho server REST.

- Secret key: dùng ký và xác minh token (production nên dùng biến môi trường).
- Algorithm: HS256 (đối xứng), phù hợp single-server.
- Expiration: thời hạn token (giây).
"""
import os

# Secret key: ưu tiên biến môi trường JWT_SECRET_KEY, fallback cho development
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
# Token hết hạn sau 1 giờ (3600 giây)
JWT_ACCESS_TOKEN_EXPIRE_SECONDS = int(
    os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_SECONDS", "3600")
)

# Định nghĩa role và quyền (RBAC)
# Role càng cao số càng lớn (để so sánh "ít nhất role X")
ROLES = {
    "guest": 0,
    "student": 1,
    "teacher": 2,
    "admin": 3,
}

# Tên role hợp lệ
VALID_ROLES = set(ROLES.keys())
