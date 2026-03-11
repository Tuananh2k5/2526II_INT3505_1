from flask import Flask, jsonify, request, url_for


def create_app() -> Flask:
    """
    Tạo Flask app với cấu trúc RESTful rõ ràng, nhất quán, dễ mở rộng.

    - Base path có versioning: /api/v1
    - Resource naming: danh từ số nhiều, lowercase, sử dụng hyphen khi cần.
    - Ví dụ resource: books
    """
    app = Flask(__name__)

    # "CSDL" giả lập trong bộ nhớ để demo.
    # Trong thực tế sẽ là database thật, layer repository, v.v.
    books = {}
    next_book_id = 1

    API_PREFIX = "/api/v1"

    def _make_book_response(book_id: int, book_data: dict, status_code: int = 200):
        """
        Trả về book kèm đường dẫn tự tham chiếu (self link) theo chuẩn REST (HATEOAS ở mức đơn giản).
        """
        response_body = {
            "id": book_id,
            "title": book_data["title"],
            "author": book_data["author"],
            "links": {
                "self": url_for("get_book", book_id=book_id, _external=False),
                "collection": url_for("list_books", _external=False),
            },
        }
        return jsonify(response_body), status_code

    @app.route(f"{API_PREFIX}/health-check", methods=["GET"])
    def health_check():
        """
        GET /api/v1/health-check

        Endpoint đơn giản để kiểm tra server đang chạy.
        Tên endpoint lowercase và dùng hyphen để phân tách từ (health-check).
        """
        return jsonify({"status": "ok"}), 200

    @app.route(f"{API_PREFIX}/books", methods=["GET"])
    def list_books():
        """
        GET /api/v1/books

        Trả về danh sách tất cả book.
        - Resource ở dạng số nhiều: "books".
        - Có thể dễ dàng mở rộng query param (ví dụ: ?author=..., ?page=...).
        """
        author_filter = request.args.get("author")

        result = []
        for book_id, book in books.items():
            if author_filter and book["author"] != author_filter:
                continue
            result.append(
                {
                    "id": book_id,
                    "title": book["title"],
                    "author": book["author"],
                    "links": {
                        "self": url_for("get_book", book_id=book_id, _external=False)
                    },
                }
            )

        return jsonify({"items": result, "total": len(result)}), 200

    @app.route(f"{API_PREFIX}/books", methods=["POST"])
    def create_book():
        """
        POST /api/v1/books

        Tạo mới một book.
        Body JSON ví dụ:
        {
            "title": "Clean Code",
            "author": "Robert C. Martin"
        }
        """
        nonlocal next_book_id

        data = request.get_json(silent=True) or {}
        title = data.get("title")
        author = data.get("author")

        if not title or not author:
            return (
                jsonify(
                    {
                        "error": "invalid-request-body",
                        "message": "Fields 'title' and 'author' are required.",
                    }
                ),
                400,
            )

        book_id = next_book_id
        books[book_id] = {"title": title, "author": author}
        next_book_id += 1

        return _make_book_response(book_id, books[book_id], status_code=201)

    @app.route(f"{API_PREFIX}/books/<int:book_id>", methods=["GET"])
    def get_book(book_id: int):
        """
        GET /api/v1/books/<book_id>

        Trả về thông tin chi tiết một book.
        """
        book = books.get(book_id)
        if not book:
            return (
                jsonify(
                    {
                        "error": "book-not-found",
                        "message": f"Book with id={book_id} does not exist.",
                    }
                ),
                404,
            )

        return _make_book_response(book_id, book, status_code=200)

    @app.route(f"{API_PREFIX}/books/<int:book_id>", methods=["PUT"])
    def update_book(book_id: int):
        """
        PUT /api/v1/books/<book_id>

        Cập nhật toàn bộ thông tin book.
        Body JSON ví dụ:
        {
            "title": "New Title",
            "author": "New Author"
        }
        """
        book = books.get(book_id)
        if not book:
            return (
                jsonify(
                    {
                        "error": "book-not-found",
                        "message": f"Book with id={book_id} does not exist.",
                    }
                ),
                404,
            )

        data = request.get_json(silent=True) or {}
        title = data.get("title")
        author = data.get("author")

        if not title or not author:
            return (
                jsonify(
                    {
                        "error": "invalid-request-body",
                        "message": "Fields 'title' and 'author' are required.",
                    }
                ),
                400,
            )

        book["title"] = title
        book["author"] = author

        return _make_book_response(book_id, book, status_code=200)

    @app.route(f"{API_PREFIX}/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id: int):
        """
        DELETE /api/v1/books/<book_id>

        Xóa một book.
        """
        book = books.pop(book_id, None)
        if not book:
            return (
                jsonify(
                    {
                        "error": "book-not-found",
                        "message": f"Book with id={book_id} does not exist.",
                    }
                ),
                404,
            )

        return "", 204

    return app


if __name__ == "__main__":
    app = create_app()
    # Dùng port khác để không trùng với các demo khác, ví dụ 5004.
    app.run(debug=True, port=5004)

