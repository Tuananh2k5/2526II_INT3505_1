"""
Script khởi tạo database: tạo bảng và seed user/role/courses/grades.
Chạy: python init_db.py
Có thể xóa file app.db rồi chạy lại để reset dữ liệu.
"""
import database as db

if __name__ == "__main__":
    db.init_db()
    print("Database đã khởi tạo (app.db). User mặc định: admin/admin123, teacher1/teacher1, student1/student1, guest1/guest1.")
