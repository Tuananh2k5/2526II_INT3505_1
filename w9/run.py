# run.py
# -------------------------------------------------------
# Entry Point của ứng dụng Flask
#
# Chạy server:
#   python run.py
#
# Các endpoint có sẵn:
#   [URL Versioning]
#   POST /api/v1/payments         => Thanh toán v1 (DEPRECATED)
#   GET  /api/v1/payments         => Danh sách giao dịch v1
#   POST /api/v2/payments         => Thanh toán v2 (STABLE)
#   GET  /api/v2/payments         => Danh sách giao dịch v2 (có phân trang)
#
#   [Query Param Versioning — Tham khảo]
#   POST /api/payments?version=1  => Thanh toán v1 qua query param
#   POST /api/payments?version=2  => Thanh toán v2 qua query param
#   GET  /api/payments?version=2  => Thông tin endpoint
# -------------------------------------------------------

from app import create_app

# Tạo Flask app instance thông qua factory function
app = create_app()

if __name__ == "__main__":
    # debug=True: bật hot-reload và hiển thị traceback chi tiết
    # Chỉ dùng debug=True trong môi trường DEVELOPMENT
    app.run(debug=True, host="0.0.0.0", port=5000)
