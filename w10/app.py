"""
============================================================
  Flask Demo: Service Operation – Security & Monitoring
  ============================================================
  Các tính năng được tích hợp:
    1. Structured Logging  → structlog + logging (console & file)
    2. Prometheus Metrics  → prometheus_flask_exporter (/metrics)
    3. Rate Limiting       → Flask-Limiter (5 req/min trên /api/secure)
    4. Circuit Breaker     → pybreaker (giả lập external service)
============================================================
"""

import logging
import random
import time
from logging.handlers import RotatingFileHandler

import pybreaker  # type: ignore
import structlog  # type: ignore
from flask import Flask, g, jsonify, request
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore
from prometheus_flask_exporter import PrometheusMetrics  # type: ignore

# ──────────────────────────────────────────────
# 1. CẤU HÌNH LOGGING
#    - Ghi ra console (StreamHandler)
#    - Ghi ra file app.log (RotatingFileHandler)
#    - Format: timestamp | level | ip | method | path | message
# ──────────────────────────────────────────────

LOG_FILE = "app.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# --- Root Python logger ---
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Handler: Console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# Handler: File (max 5MB × 3 backups)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# --- structlog wrapper (thêm context fields tự động) ---
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger("app")

# ──────────────────────────────────────────────
# 2. KHỞI TẠO FLASK APP
# ──────────────────────────────────────────────

app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-secret-key-change-in-prod"

# ──────────────────────────────────────────────
# 3. PROMETHEUS METRICS
#    - Tự động theo dõi tất cả endpoint
#    - Expose tại GET /metrics
# ──────────────────────────────────────────────

metrics = PrometheusMetrics(app, path='/metrics')
# Thêm info metric tĩnh về phiên bản app
metrics.info("app_info", "Application information", version="1.0.0", environment="demo")

# ──────────────────────────────────────────────
# 4. RATE LIMITER
#    - Mặc định: 200 req/ngày, 50 req/giờ
#    - /api/secure: giới hạn riêng 5 req/phút
#    - Lưu state trong memory (thay bằng Redis cho production)
# ──────────────────────────────────────────────

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ──────────────────────────────────────────────
# 5. CIRCUIT BREAKER
#    - fail_max=3: mở mạch sau 3 lỗi liên tiếp
#    - reset_timeout=15: tự thử lại sau 15 giây
# ──────────────────────────────────────────────

# Listener để log trạng thái circuit breaker
class CBListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        log.warning(
            "circuit_breaker_state_change",
            breaker=cb.name,
            old=old_state.name,
            new=new_state.name,
        )

external_service_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=15,
    name="external_service",
    listeners=[CBListener()],
)


def call_external_service():
    """
    Hàm giả lập gọi một external service không ổn định.
    Xác suất thất bại: 80% → để dễ trigger Circuit Breaker.
    """
    if random.random() < 0.8:  # 80% lỗi
        raise ConnectionError("External service is unavailable!")
    return {"data": "response from external service", "latency_ms": random.randint(50, 200)}


@external_service_breaker
def protected_call():
    """Wrap hàm gọi service bằng circuit breaker."""
    return call_external_service()


# ──────────────────────────────────────────────
# 6. REQUEST HOOKS – LOG MỌI REQUEST
# ──────────────────────────────────────────────

@app.before_request
def log_request_start():
    """Ghi log trước khi xử lý mỗi request."""
    g.start_time = time.time()
    log.info(
        "request_started",
        ip=request.remote_addr,
        method=request.method,
        path=request.path,
        user_agent=request.headers.get("User-Agent", "-"),
    )


@app.after_request
def log_request_end(response):
    """Ghi log sau khi xử lý xong, bao gồm thời gian xử lý."""
    duration_ms = round((time.time() - g.start_time) * 1000, 2)
    log.info(
        "request_finished",
        ip=request.remote_addr,
        method=request.method,
        path=request.path,
        status=response.status_code,
        duration_ms=duration_ms,
    )
    return response


# ──────────────────────────────────────────────
# 7. ENDPOINTS
# ──────────────────────────────────────────────

# GET /  – Trang chủ
@app.route("/")
def index():
    """Trang chủ – giới thiệu các endpoint có sẵn."""
    log.info("home_accessed", ip=request.remote_addr)
    return jsonify({
        "service": "Flask Security & Monitoring Demo",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Trang chủ (bạn đang ở đây)",
            "GET /api/data": "Endpoint bình thường, có logging chi tiết",
            "GET /api/secure": "Endpoint có Rate Limit: 5 req/phút",
            "GET /api/external": "Endpoint có Circuit Breaker (giả lập lỗi 80%)",
            "GET /metrics": "Prometheus metrics endpoint",
        },
    })


# GET /api/data – Endpoint bình thường
@app.route("/api/data")
def api_data():
    """Endpoint bình thường – minh họa logging có cấu trúc."""
    log.info("api_data_called", ip=request.remote_addr, method=request.method)
    payload = {
        "message": "Đây là dữ liệu từ /api/data",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note": "Request này đã được ghi vào app.log và console.",
    }
    return jsonify(payload), 200


# GET /api/secure – Endpoint có Rate Limit
@app.route("/api/secure")
@limiter.limit("5 per minute")  # ← Giới hạn: chỉ 5 request mỗi phút từ cùng 1 IP
def api_secure():
    """
    Endpoint bảo mật với Rate Limiting.
    Nếu vượt quá 5 req/phút, Flask-Limiter sẽ tự trả về HTTP 429.
    """
    log.info("api_secure_called", ip=request.remote_addr)
    return jsonify({
        "message": "Truy cập thành công vào endpoint được bảo vệ!",
        "info": "Endpoint này giới hạn 5 request/phút mỗi IP.",
        "tip": "Gọi thêm 5 lần nữa để thấy lỗi HTTP 429 Too Many Requests.",
    }), 200


# Handler lỗi Rate Limit (tùy chỉnh response)
@app.errorhandler(429)
def ratelimit_error(e):
    log.warning("rate_limit_exceeded", ip=request.remote_addr, path=request.path, limit=str(e.description))
    return jsonify({
        "error": "Too Many Requests",
        "message": "Bạn đã vượt quá giới hạn request. Hãy thử lại sau 1 phút.",
        "retry_after": "60 seconds",
    }), 429


# GET /api/external – Endpoint có Circuit Breaker
@app.route("/api/external")
def api_external():
    """
    Endpoint giả lập gọi external service.
    - Xác suất lỗi: 80%
    - Sau 3 lỗi liên tiếp: Circuit Breaker chuyển sang OPEN
    - Sau 15 giây: Circuit Breaker chuyển sang HALF-OPEN để thử lại
    """
    try:
        result = protected_call()
        log.info("external_service_success", result=result)
        return jsonify({
            "status": "success",
            "circuit_breaker": "CLOSED (hoạt động bình thường)",
            "data": result,
        }), 200

    except pybreaker.CircuitBreakerError:
        # Circuit đang MỞ (OPEN) – không cho phép gọi thêm
        log.error("circuit_breaker_open", ip=request.remote_addr, path="/api/external")
        return jsonify({
            "status": "error",
            "circuit_breaker": "OPEN (đã ngắt mạch!)",
            "message": "Service bên ngoài đang không khả dụng. Circuit Breaker đã kích hoạt.",
            "retry_after": "15 seconds",
        }), 503

    except ConnectionError as e:
        # Lỗi thông thường (circuit vẫn đang đếm)
        log.error("external_service_failed", error=str(e), ip=request.remote_addr)
        return jsonify({
            "status": "error",
            "circuit_breaker": "CLOSED (đang đếm lỗi...)",
            "message": f"Lỗi kết nối tới external service: {e}",
        }), 502


# ──────────────────────────────────────────────
# 8. ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    log.info("app_starting", host="0.0.0.0", port=5000, debug=True)
    # Tắt reloader để tránh lỗi multiprocess của Prometheus metrics
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
