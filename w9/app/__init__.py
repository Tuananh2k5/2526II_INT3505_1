# app/__init__.py
# -------------------------------------------------------
# Application Factory Pattern
# Cho phép tạo nhiều instance của app (hữu ích cho testing),
# và giúp tránh circular imports khi dùng Blueprint.
# -------------------------------------------------------

from flask import Flask
from .api.v1.payments import v1_blueprint
from .api.v2.payments import v2_blueprint
from .api.versioned.payments import versioned_blueprint


def create_app():
    """
    Factory function để khởi tạo Flask application.
    Đăng ký các Blueprint tương ứng với từng phiên bản API.
    """
    app = Flask(__name__)

    # -------------------------------------------------------
    # Đăng ký Blueprint cho API v1
    # url_prefix='/api/v1' => tất cả route trong v1_blueprint
    # đều có tiền tố /api/v1/...
    # -------------------------------------------------------
    app.register_blueprint(v1_blueprint, url_prefix="/api/v1")

    # -------------------------------------------------------
    # Đăng ký Blueprint cho API v2
    # url_prefix='/api/v2' => tất cả route trong v2_blueprint
    # đều có tiền tố /api/v2/...
    # -------------------------------------------------------
    app.register_blueprint(v2_blueprint, url_prefix="/api/v2")

    # -------------------------------------------------------
    # Đăng ký Blueprint minh hoạ Query Parameter Versioning
    # url_prefix='/api' => route /api/payments?version=1 hoặc 2
    # -------------------------------------------------------
    app.register_blueprint(versioned_blueprint, url_prefix="/api")

    return app
