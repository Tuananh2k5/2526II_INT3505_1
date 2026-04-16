from models import db, Product
from flask import abort

def get_products():
    """Lấy danh sách tất cả sản phẩm"""
    products = Product.query.all()
    return [p.to_dict() for p in products]

def create_product(body):
    """Tạo sản phẩm mới"""
    new_product = Product(
        name=body['name'],
        price=body['price'],
        description=body.get('description', '')
    )
    db.session.add(new_product)
    db.session.commit()
    return new_product.to_dict(), 201

def get_product(id):
    """Lấy thông tin chi tiết một sản phẩm theo ID"""
    product = Product.query.get(id)
    if product is None:
        abort(404, description=f"Product with id {id} not found")
    return product.to_dict()

def update_product(id, body):
    """Cập nhật thông tin sản phẩm"""
    product = Product.query.get(id)
    if product is None:
        abort(404, description=f"Product with id {id} not found")
    
    # Cập nhật các trường được truyền đến
    if 'name' in body:
        product.name = body['name']
    if 'price' in body:
        product.price = body['price']
    if 'description' in body:
        product.description = body['description']
        
    db.session.commit()
    return product.to_dict()

def delete_product(id):
    """Xoá một sản phẩm"""
    product = Product.query.get(id)
    if product is None:
        abort(404, description=f"Product with id {id} not found")
        
    db.session.delete(product)
    db.session.commit()
    return '', 204
