import pytest
from app import app, products

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_data():
    products.clear()
    products.extend([
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
        {"id": 2, "name": "Mouse", "price": 25.50, "stock": 100}
    ])
    import app as my_app
    my_app.next_id = 3

def test_get_all_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_get_specific_product(client):
    response = client.get('/api/products/1')
    assert response.status_code == 200
    assert response.json['name'] == 'Laptop'

def test_get_product_not_found(client):
    response = client.get('/api/products/999')
    assert response.status_code == 404
    assert response.json['error'] == 'Product not found'

def test_create_product(client):
    new_product = {"name": "Keyboard", "price": 45.0, "stock": 50}
    response = client.post('/api/products', json=new_product)
    assert response.status_code == 201
    assert response.json['id'] == 3
    assert response.json['name'] == 'Keyboard'

def test_create_product_missing_fields(client):
    new_product = {"name": "Keyboard", "price": 45.0}
    response = client.post('/api/products', json=new_product)
    assert response.status_code == 400

def test_update_product(client):
    update_data = {"price": 899.99}
    response = client.put('/api/products/1', json=update_data)
    assert response.status_code == 200
    assert response.json['price'] == 899.99

def test_update_product_not_found(client):
    response = client.put('/api/products/999', json={"price": 10.0})
    assert response.status_code == 404

def test_delete_product(client):
    response = client.delete('/api/products/1')
    assert response.status_code == 204
    get_response = client.get('/api/products/1')
    assert get_response.status_code == 404

def test_delete_product_not_found(client):
    response = client.delete('/api/products/999')
    assert response.status_code == 404
