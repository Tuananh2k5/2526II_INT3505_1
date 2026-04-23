from locust import HttpUser, task, between
import random

class ProductAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(4)
    def view_products(self):
        self.client.get("/api/products")

    @task(2)
    def view_single_product(self):
        product_id = random.choice([1, 2])
        self.client.get(f"/api/products/{product_id}", name="/api/products/[id]")

    @task(1)
    def create_product(self):
        self.client.post("/api/products", json={
            "name": f"Test Product {random.randint(100, 999)}",
            "price": round(random.uniform(10.0, 100.0), 2),
            "stock": random.randint(1, 50)
        })
