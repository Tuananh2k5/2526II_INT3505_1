from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import yaml
from flask import Flask, Response, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint


# =========================
# App setup
# =========================
app = Flask(__name__)

@app.get("/")
def index():
    return jsonify({
        "message": "Welcome to Book Manager API! Go to /docs for Swagger UI.",
        "status": "ok"
    })

# Đường dẫn tới file OpenAPI. Dùng đường dẫn tuyệt đối để chạy từ bất kỳ cwd nào.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAPI_PATH = os.path.join(BASE_DIR, "openapi.yaml")


# =========================
# In-memory "database"
# =========================
@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    createdAt: str
    updatedAt: str | None = None



# Author dataclass và "database"
@dataclass
class Author:
    id: int
    name: str
    createdAt: str
    updatedAt: str | None = None

_books: dict[int, Book] = {}
_next_id: int = 1
_authors: dict[int, Author] = {}
_author_next_id: int = 1


def _now_iso() -> str:
    # Chuẩn hóa datetime dạng ISO-8601 UTC để phù hợp OpenAPI schema (date-time).
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error(status_code: int, error: str, message: str):
    return jsonify({"error": error, "message": message}), status_code


def _parse_int(value: Any, default: int, *, min_value: int | None = None, max_value: int | None = None) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    if min_value is not None and n < min_value:
        return default
    if max_value is not None and n > max_value:
        return default
    return n



def _validate_book_payload(payload: Any) -> tuple[dict[str, Any] | None, tuple[Response, int] | None]:
    # Validate theo schema: title (str, non-empty), author (str, non-empty), year (int >= 0)
    if not isinstance(payload, dict):
        return None, _error(400, "BAD_REQUEST", "Body must be a JSON object")

    title = payload.get("title")
    author = payload.get("author")
    year = payload.get("year")

    if not isinstance(title, str) or not title.strip():
        return None, _error(400, "BAD_REQUEST", "Field 'title' is required and must be a non-empty string")
    if not isinstance(author, str) or not author.strip():
        return None, _error(400, "BAD_REQUEST", "Field 'author' is required and must be a non-empty string")
    if not isinstance(year, int) or year < 0:
        return None, _error(400, "BAD_REQUEST", "Field 'year' is required and must be an integer >= 0")

    return {"title": title.strip(), "author": author.strip(), "year": year}, None

def _validate_author_payload(payload: Any) -> tuple[dict[str, Any] | None, tuple[Response, int] | None]:
    # Validate: name (str, non-empty)
    if not isinstance(payload, dict):
        return None, _error(400, "BAD_REQUEST", "Body must be a JSON object")
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return None, _error(400, "BAD_REQUEST", "Field 'name' is required and must be a non-empty string")
    return {"name": name.strip()}, None


# Seed data để test nhanh.
def _seed():
    global _next_id, _author_next_id
    # Seed authors
    author_samples = [
        {"name": "Robert C. Martin"},
        {"name": "Andrew Hunt & David Thomas"},
    ]
    for s in author_samples:
        author_id = _author_next_id
        _author_next_id += 1
        _authors[author_id] = Author(id=author_id, name=s["name"], createdAt=_now_iso())

    # Seed books
    book_samples = [
        {"title": "Clean Code", "author": "Robert C. Martin", "year": 2008},
        {"title": "The Pragmatic Programmer", "author": "Andrew Hunt & David Thomas", "year": 1999},
    ]
    for s in book_samples:
        book_id = _next_id
        _next_id += 1
        _books[book_id] = Book(id=book_id, createdAt=_now_iso(), **s)

_seed()
# =========================
# API endpoints (5 endpoints)
# =========================

# ===== CRUD cho Author =====
@app.get("/api/authors")
def list_authors():
    """
    Lấy danh sách author, hỗ trợ phân trang (limit, offset) và tìm kiếm (q theo name)
    """
    limit = _parse_int(request.args.get("limit"), 10, min_value=1, max_value=100)
    offset = _parse_int(request.args.get("offset"), 0, min_value=0)
    q = request.args.get("q", "")
    q = q.strip().lower() if isinstance(q, str) else ""

    items = list(_authors.values())
    if q:
        items = [a for a in items if q in a.name.lower()]
    total = len(items)
    items = items[offset : offset + limit]
    return jsonify({
        "items": [asdict(a) for a in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    })

@app.post("/api/authors")
def create_author():
    global _author_next_id
    payload = request.get_json(silent=True)
    data, err = _validate_author_payload(payload)
    if err:
        return err
    author_id = _author_next_id
    _author_next_id += 1
    author = Author(id=author_id, name=data["name"], createdAt=_now_iso())
    _authors[author_id] = author
    return jsonify(asdict(author)), 201

@app.get("/api/authors/<int:author_id>")
def get_author(author_id: int):
    author = _authors.get(author_id)
    if not author:
        return _error(404, "NOT_FOUND", "Author not found")
    return jsonify(asdict(author))

@app.put("/api/authors/<int:author_id>")
def update_author(author_id: int):
    author = _authors.get(author_id)
    if not author:
        return _error(404, "NOT_FOUND", "Author not found")
    payload = request.get_json(silent=True)
    data, err = _validate_author_payload(payload)
    if err:
        return err
    author.name = data["name"]
    author.updatedAt = _now_iso()
    return jsonify(asdict(author))

@app.delete("/api/authors/<int:author_id>")
def delete_author(author_id: int):
    if author_id not in _authors:
        return _error(404, "NOT_FOUND", "Author not found")
    del _authors[author_id]
    return ("", 204)


# =========================
# OpenAPI + Swagger UI
# =========================
@app.get("/openapi.yaml")
def openapi_yaml():
    # Trả về nội dung spec (yaml) để Swagger UI có thể load.
    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="application/yaml")


SWAGGER_URL = "/docs"  # Swagger UI endpoint
API_URL = "/openapi.yaml"  # OpenAPI spec endpoint

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Book Manager API (Swagger UI)",
    },
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# =========================
# API endpoints (5 endpoints)
# =========================
@app.get("/api/books")
def list_books():
    """
    List books with basic pagination + search.
    Query params are documented in openapi.yaml:
      - limit, offset, q
    """
    limit = _parse_int(request.args.get("limit"), 10, min_value=1, max_value=100)
    offset = _parse_int(request.args.get("offset"), 0, min_value=0)
    q = request.args.get("q", "")
    q = q.strip().lower() if isinstance(q, str) else ""

    items = list(_books.values())
    if q:
        items = [b for b in items if (q in b.title.lower() or q in b.author.lower())]

    total = len(items)
    items = items[offset : offset + limit]
    return jsonify(
        {
            "items": [asdict(b) for b in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


@app.post("/api/books")
def create_book():
    global _next_id
    payload = request.get_json(silent=True)
    data, err = _validate_book_payload(payload)
    if err:
        return err

    book_id = _next_id
    _next_id += 1

    book = Book(
        id=book_id,
        title=data["title"],
        author=data["author"],
        year=data["year"],
        createdAt=_now_iso(),
    )
    _books[book_id] = book
    return jsonify(asdict(book)), 201


@app.get("/api/books/<int:book_id>")
def get_book(book_id: int):
    book = _books.get(book_id)
    if not book:
        return _error(404, "NOT_FOUND", "Book not found")
    return jsonify(asdict(book))


@app.put("/api/books/<int:book_id>")
def update_book(book_id: int):
    book = _books.get(book_id)
    if not book:
        return _error(404, "NOT_FOUND", "Book not found")

    payload = request.get_json(silent=True)
    data, err = _validate_book_payload(payload)
    if err:
        return err

    book.title = data["title"]
    book.author = data["author"]
    book.year = data["year"]
    book.updatedAt = _now_iso()
    return jsonify(asdict(book))


@app.delete("/api/books/<int:book_id>")
def delete_book(book_id: int):
    if book_id not in _books:
        return _error(404, "NOT_FOUND", "Book not found")
    del _books[book_id]
    return ("", 204)


# =========================
# Optional: validate OpenAPI at startup (dev-friendly)
# =========================
def _validate_openapi_file():
    # Kiểm tra file YAML có parse được hay không; không validate schema đầy đủ.
    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        yaml.safe_load(f)


_validate_openapi_file()


if __name__ == "__main__":
    # Chạy dev server:
    # - Swagger UI: http://localhost:5000/docs
    # - Spec:       http://localhost:5000/openapi.yaml
    # - API:        /api/books...
    app.run(host="0.0.0.0", port=5000, debug=True)
