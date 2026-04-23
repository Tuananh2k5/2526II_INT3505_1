from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory database
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    {"id": 2, "name": "Mouse", "price": 25.50, "stock": 100}
]
next_id = 3

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products), 200

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/products', methods=['POST'])
def create_product():
    global next_id
    data = request.get_json()
    
    if not data or not all(k in data for k in ("name", "price", "stock")):
        return jsonify({"error": "Missing required fields"}), 400
        
    if not isinstance(data["price"], (int, float)) or not isinstance(data["stock"], int):
        return jsonify({"error": "Invalid data types"}), 400

    new_product = {
        "id": next_id,
        "name": data["name"],
        "price": float(data["price"]),
        "stock": data["stock"]
    }
    products.append(new_product)
    next_id += 1
    
    return jsonify(new_product), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        product["name"] = data["name"]
    if "price" in data:
        if not isinstance(data["price"], (int, float)):
            return jsonify({"error": "Invalid price"}), 400
        product["price"] = float(data["price"])
    if "stock" in data:
        if not isinstance(data["stock"], int):
            return jsonify({"error": "Invalid stock"}), 400
        product["stock"] = data["stock"]
        
    return jsonify(product), 200

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products
    initial_length = len(products)
    products = [p for p in products if p['id'] != product_id]
    
    if len(products) < initial_length:
        return '', 204
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
