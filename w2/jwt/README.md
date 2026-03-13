# JWT REST API (w2/jwt)

Flask server minh họa **JWT** (encode, decode) và **RBAC** (Role-Based Access Control) theo nguyên tắc **REST** (stateless, resource naming, HTTP verbs và status codes), **dùng dữ liệu thực từ SQLite** (user, role, courses, grades).

## Cài đặt

```bash
cd w2/jwt
pip install -r requirements.txt
```

## Chạy server

```bash
python app.py
```

Server chạy tại `http://localhost:5004`.

## Kiến trúc REST

- **Base path có version:** `/api/v1`
- **Tài nguyên auth:** `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `GET /api/v1/auth/verify`
- **Stateless:** Mỗi request bảo vệ phải gửi header `Authorization: Bearer <access_token>`
- **RBAC:** Các endpoint `/admin/*`, `/teachers/*`, `/students/*` kiểm tra role trong token

## Chức năng JWT + dữ liệu thực

| Chức năng   | Mô tả |
|------------|--------|
| **Encode** | `POST /api/v1/auth/login` — đọc user từ **SQLite**, so sánh **password hash (scrypt)**, sau đó tạo JWT chứa `sub`, `username`, `role` |
| **Decode** | `GET /api/v1/auth/me`, `GET /api/v1/auth/verify` — xác thực token và trích payload (sub, role, ...). `/me` có thể sync role mới nhất từ DB |
| **RBAC**   | `@require_roles(\"admin\")`, `@require_min_role(\"teacher\")` — kiểm tra role trong token; admin/teacher/student được map từ bảng `roles` trong DB |

## Database thực tế

- File DB: `w2/jwt/app.db` (SQLite, tự tạo khi chạy app lần đầu).
- Khởi tạo trong `database.py`:
  - Bảng `roles` (guest, student, teacher, admin, có `level` dùng cho RBAC).
  - Bảng `users` (username, password_hash, role_id).
  - Bảng `courses` (khóa học thật).
  - Bảng `grades` (điểm thật của sinh viên).
- Seed ban đầu:
  - admin: username `admin`, password `admin123`, role `admin`.
  - teacher1: username `teacher1`, password `teacher1`, role `teacher`.
  - student1: username `student1`, password `student1`, role `student`.
  - guest1: username `guest1`, password `guest1`, role `guest`.

> Lưu ý: mật khẩu lưu trong DB luôn ở dạng hash (scrypt), **không lưu plaintext**. Các password ở trên chỉ để bạn biết cách đăng nhập test.

## Test nhanh (curl / PowerShell)

**1. Health (không cần token):**
```bash
curl http://localhost:5004/api/v1/health
```

**2. Login (encode JWT):**
```bash
curl -X POST http://localhost:5004/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```
Lấy `access_token` từ response.

**3. Me (decode token):**
```bash
curl http://localhost:5004/api/v1/auth/me -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**4. Verify token:**
```bash
curl http://localhost:5004/api/v1/auth/verify -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**5. RBAC — Admin only (dữ liệu thực từ DB):**
```bash
curl http://localhost:5004/api/v1/admin/dashboard -H "Authorization: Bearer <TOKEN_ADMIN>"
# Token student -> 403 Forbidden
```

**6. RBAC — Teacher trở lên:**
```bash
curl http://localhost:5004/api/v1/teachers/courses -H "Authorization: Bearer <TOKEN_TEACHER_OR_ADMIN>"
```

**7. RBAC — Student/Teacher/Admin xem điểm thật từ DB:**
```bash
curl http://localhost:5004/api/v1/students/grades -H "Authorization: Bearer <TOKEN_STUDENT_OR_TEACHER_OR_ADMIN>"
```

## Cấu trúc thư mục

```
w2/jwt/
├── app.py           # Flask app, routes REST
├── database.py      # SQLite + password hash + user/role/courses/grades thực tế
├── config.py        # JWT secret, algorithm, expiration, ROLES
├── jwt_utils.py     # encode_token(), decode_token()
├── auth.py          # get_current_user(), require_roles(), require_min_role()
├── requirements.txt
└── README.md
```

## Cấu hình (config.py)

- `JWT_SECRET_KEY`: biến môi trường `JWT_SECRET_KEY` hoặc giá trị mặc định (chỉ dùng cho dev).
- `JWT_ACCESS_TOKEN_EXPIRE_SECONDS`: thời hạn token (mặc định 3600 giây).
