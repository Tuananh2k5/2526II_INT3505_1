"""
MINH HỌA NGUYÊN TẮC UNIFORM INTERFACE CỦA REST
==============================================
Uniform Interface gồm 4 thành phần chính:
1. Resource Identification (Định danh tài nguyên bằng URI)
2. Manipulation through representations (Thao tác qua biểu diễn - JSON/XML)
3. Self-descriptive messages (Thông điệp tự mô tả - HTTP methods, headers, status)
4. HATEOAS - Hypermedia (Links trong response để client khám phá API)
"""

from flask import Flask, request, jsonify, url_for

app = Flask(__name__)

# ========== 1. RESOURCE IDENTIFICATION (Định danh tài nguyên bằng URI) ==========
# Mỗi resource có URI duy nhất, nhất quán: /api/<tên-collection>/<id>

PRODUCTS = {
    1: {"id": 1, "name": "Laptop", "price": 15000000},
    2: {"id": 2, "name": "Phone", "price": 8000000},
}


def _product_links(product_id):
    """HATEOAS: links để client biết có thể làm gì tiếp theo."""
    return {
        "self": url_for("get_product", product_id=product_id, _external=True),
        "collection": url_for("list_products", _external=True),
        "update": url_for("update_product", product_id=product_id, _external=True),
        "delete": url_for("delete_product", product_id=product_id, _external=True),
    }


# ========== 2 & 3. UNIFORM INTERFACE: Cùng URI, khác HTTP METHOD ==========
# Self-descriptive: method (GET/POST/PUT/DELETE) + Content-Type mô tả ý nghĩa

@app.route("/api/products", methods=["GET"])
def list_products():
    """GET /api/products -> Lấy danh sách (Read)."""
    items = [
        {**p, "_links": _product_links(p["id"])}
        for p in PRODUCTS.values()
    ]
    return jsonify({
        "count": len(items),
        "products": items,
        "_links": {"self": url_for("list_products", _external=True)},
    })


@app.route("/api/products", methods=["POST"])
def create_product():
    """POST /api/products + body -> Tạo mới (Create)."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400
    new_id = max(PRODUCTS.keys(), default=0) + 1
    PRODUCTS[new_id] = {
        "id": new_id,
        "name": data["name"],
        "price": data.get("price", 0),
    }
    # 201 Created + Location header (chuẩn REST)
    return (
        jsonify({**PRODUCTS[new_id], "_links": _product_links(new_id)}),
        201,
        {"Location": url_for("get_product", product_id=new_id, _external=True)},
    )


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """GET /api/products/<id> -> Lấy một resource (Read)."""
    if product_id not in PRODUCTS:
        return jsonify({"error": "Not found"}), 404
    p = {**PRODUCTS[product_id], "_links": _product_links(product_id)}
    return jsonify(p)


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """PUT /api/products/<id> + body -> Cập nhật toàn bộ (Update)."""
    if product_id not in PRODUCTS:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json() or {}
    PRODUCTS[product_id].update({
        "name": data.get("name", PRODUCTS[product_id]["name"]),
        "price": data.get("price", PRODUCTS[product_id]["price"]),
    })
    return jsonify({**PRODUCTS[product_id], "_links": _product_links(product_id)})


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """DELETE /api/products/<id> -> Xóa resource."""
    if product_id not in PRODUCTS:
        return jsonify({"error": "Not found"}), 404
    del PRODUCTS[product_id]
    return "", 204  # No Content (chuẩn REST khi delete thành công)


# ========== ĐIỂM NHẤN UNIFORM INTERFACE ==========
# - Cùng base URI /api/products (và /api/products/<id>)
# - Ý nghĩa thay đổi theo HTTP method (GET=read, POST=create, PUT=update, DELETE=delete)
# - Request/Response đều là "representation" (JSON), self-descriptive (Content-Type: application/json)
# - Status code chuẩn: 200, 201, 204, 400, 404
# - HATEOAS: _links trong response để client biết bước tiếp theo

if __name__ == "__main__":
    app.run(debug=True)
