"""
MINH HỌA NGUYÊN TẮC CACHEABLE CỦA REST
======================================
- Mục tiêu: Cho client / proxy biết response có thể cache được hay không, cache bao lâu,
  và làm sao để kiểm tra dữ liệu có thay đổi hay chưa (ETag / Last-Modified).
- Lợi ích: Giảm số request, giảm băng thông, tăng tốc độ phản hồi.
"""

from datetime import datetime
import hashlib
import json

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


# "Cơ sở dữ liệu" giả lập trong bộ nhớ
NEWS = {
    1: {
        "id": 1,
        "title": "REST là gì?",
        "content": "REST là phong cách kiến trúc cho các dịch vụ web.",
        "updated_at": datetime(2025, 1, 1, 10, 0, 0),
    },
    2: {
        "id": 2,
        "title": "Cacheable trong REST",
        "content": "Response nên khai báo rõ ràng có được cache hay không.",
        "updated_at": datetime(2025, 1, 2, 9, 30, 0),
    },
}


def _build_collection_representation():
    """Trả về representation dạng JSON cho collection NEWS."""
    items = []
    for n in NEWS.values():
        items.append(
            {
                "id": n["id"],
                "title": n["title"],
                "content": n["content"],
                "updated_at": n["updated_at"].isoformat(),
            }
        )
    return {"count": len(items), "news": items}


def _generate_etag(data: dict) -> str:
    """
    Sinh ETag từ nội dung JSON (hash MD5).
    Nếu dữ liệu không đổi -> ETag giữ nguyên -> client có thể dùng để revalidate.
    """
    body_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(body_json.encode("utf-8")).hexdigest()


@app.route("/api/cacheable/news", methods=["GET"])
def list_news_cacheable():
    """
    GET /api/cacheable/news

    Minh họa:
    - Server gắn Cache-Control, ETag, Last-Modified.
    - Client có thể gửi If-None-Match để kiểm tra dữ liệu có đổi không.
    """
    representation = _build_collection_representation()
    etag = _generate_etag(representation)

    # Nếu client gửi If-None-Match và trùng ETag -> dữ liệu KHÔNG đổi
    client_etag = request.headers.get("If-None-Match")
    if client_etag == etag:
        # 304 Not Modified: không gửi lại body, chỉ header
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "public, max-age=60"
        # Lấy mốc updated_at mới nhất để làm Last-Modified
        last_updated = max(n["updated_at"] for n in NEWS.values())
        resp.headers["Last-Modified"] = last_updated.strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        return resp

    # Lần đầu (hoặc ETag khác) -> trả data + header cache
    resp = make_response(jsonify(representation), 200)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "public, max-age=60"  # cho phép cache 60 giây
    last_updated = max(n["updated_at"] for n in NEWS.values())
    resp.headers["Last-Modified"] = last_updated.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    return resp


@app.route("/api/cacheable/news/<int:news_id>", methods=["GET"])
def get_news_cacheable(news_id: int):
    """
    GET /api/cacheable/news/<id>

    Minh họa cache cho từng resource riêng lẻ.
    """
    news = NEWS.get(news_id)
    if not news:
        return jsonify({"error": "Not found"}), 404

    representation = {
        "id": news["id"],
        "title": news["title"],
        "content": news["content"],
        "updated_at": news["updated_at"].isoformat(),
    }
    etag = _generate_etag(representation)

    client_etag = request.headers.get("If-None-Match")
    if client_etag == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "public, max-age=120"
        resp.headers["Last-Modified"] = news["updated_at"].strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        return resp

    resp = make_response(jsonify(representation), 200)
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "public, max-age=120"  # resource riêng có thể cache lâu hơn
    resp.headers["Last-Modified"] = news["updated_at"].strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    return resp


if __name__ == "__main__":
    # Chạy server riêng để demo cacheable, tránh trùng với file demo khác.
    app.run(debug=True, port=5001)

