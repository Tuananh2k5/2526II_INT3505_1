"""
Lớp truy cập dữ liệu thực: SQLite, hash mật khẩu (werkzeug), role từ DB.

- Bảng: roles, users, courses, grades.
- Phân quyền thực tế: role lấy từ DB khi login, đưa vào JWT; admin đổi role qua API.
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash

# Đường dẫn DB (cùng thư mục w2/jwt)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get("JWT_DATABASE_PATH", os.path.join(BASE_DIR, "app.db"))


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


@contextmanager
def get_db():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Tạo bảng và seed dữ liệu ban đầu nếu chưa có."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                level INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (role_id) REFERENCES roles(id)
            );
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (teacher_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                score REAL NOT NULL,
                updated_at TEXT DEFAULT (datetime('now')),
                UNIQUE(student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            );
        """)
        # Seed roles
        conn.execute(
            "INSERT OR IGNORE INTO roles (id, name, level) VALUES (1, 'guest', 0), (2, 'student', 1), (3, 'teacher', 2), (4, 'admin', 3)"
        )
        # Seed admin nếu chưa có user nào
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            admin_hash = generate_password_hash("admin123", method="scrypt")
            conn.execute(
                "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, 4)",
                ("admin", admin_hash),
            )
            # Thêm vài user mẫu
            for username, password, role_id in [
                ("teacher1", "teacher1", 3),
                ("student1", "student1", 2),
                ("guest1", "guest1", 1),
            ]:
                h = generate_password_hash(password, method="scrypt")
                conn.execute(
                    "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)",
                    (username, h, role_id),
                )
            # Khóa học do teacher1 tạo (teacher_id = 2 vì admin = 1)
            conn.execute(
                "INSERT INTO courses (name, teacher_id) VALUES ('Toán cao cấp', 2), ('Vật lý đại cương', 2)"
            )
            conn.execute(
                "INSERT INTO grades (student_id, course_id, score) VALUES (3, 1, 8.5), (3, 2, 7.0)"
            )


# --- User ---

def get_user_by_username(username: str) -> Optional[dict]:
    """Lấy user theo username (kèm tên role)."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username, u.password_hash, u.role_id, u.created_at, r.name AS role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = ?
            """,
            (username.strip(),),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "role_id": row["role_id"],
        "role": row["role_name"],
        "created_at": row["created_at"],
    }


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Lấy user theo id (dùng khi kiểm tra quyền hoặc hiển thị)."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username, u.role_id, u.created_at, r.name AS role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = ?
            """,
            (user_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "role_id": row["role_id"],
        "role": row["role_name"],
        "created_at": row["created_at"],
    }


def verify_password(user: dict, password: str) -> bool:
    """So sánh mật khẩu với hash trong DB."""
    return check_password_hash(user["password_hash"], password)


def list_users() -> list[dict]:
    """Danh sách user (admin dùng)."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT u.id, u.username, u.role_id, u.created_at, r.name AS role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            ORDER BY u.id
            """
        ).fetchall()
    return [
        {
            "id": r["id"],
            "username": r["username"],
            "role_id": r["role_id"],
            "role": r["role_name"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def update_user_role(user_id: int, role_name: str) -> bool:
    """Đổi role của user (admin). role_name: guest, student, teacher, admin."""
    with get_db() as conn:
        role_row = conn.execute("SELECT id FROM roles WHERE name = ?", (role_name,)).fetchone()
        if not role_row:
            return False
        cur = conn.execute(
            "UPDATE users SET role_id = ? WHERE id = ?",
            (role_row["id"], user_id),
        )
        updated = cur.rowcount
    return updated > 0


def create_user(username: str, password: str, role_name: str = "student") -> Optional[dict]:
    """Tạo user mới (admin hoặc register). Trả về user dict hoặc None nếu username trùng."""
    with get_db() as conn:
        role_row = conn.execute("SELECT id FROM roles WHERE name = ?", (role_name,)).fetchone()
        if not role_row:
            return None
        password_hash = generate_password_hash(password, method="scrypt")
        try:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)",
                (username.strip(), password_hash, role_row["id"]),
            )
            user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            return None
    return get_user_by_id(user_id)


# --- Courses (teacher thực tế) ---

def list_courses_by_teacher(teacher_id: int) -> list[dict]:
    """Khóa học do một teacher phụ trách."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, teacher_id, created_at FROM courses WHERE teacher_id = ? ORDER BY id",
            (teacher_id,),
        ).fetchall()
    return [{k: r[k] for k in r.keys()} for r in rows]


def list_courses_for_api(teacher_id: Optional[int] = None) -> list[dict]:
    """Tất cả khóa học; nếu teacher_id thì chỉ của teacher đó. Admin xem hết."""
    with get_db() as conn:
        if teacher_id is not None:
            rows = conn.execute(
                "SELECT id, name, teacher_id, created_at FROM courses WHERE teacher_id = ? ORDER BY id",
                (teacher_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, name, teacher_id, created_at FROM courses ORDER BY id"
            ).fetchall()
    return [{k: r[k] for k in r.keys()} for r in rows]


# --- Grades (sinh viên thực tế) ---

def list_grades_by_student(student_id: int) -> list[dict]:
    """Điểm của một sinh viên (kèm tên môn)."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT g.id, g.student_id, g.course_id, g.score, g.updated_at, c.name AS course_name
            FROM grades g
            JOIN courses c ON g.course_id = c.id
            WHERE g.student_id = ?
            ORDER BY c.name
            """,
            (student_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "course_id": r["course_id"],
            "course_name": r["course_name"],
            "score": r["score"],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


def count_users() -> int:
    """Số user (admin dashboard)."""
    with get_db() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
