from flask_sqlalchemy import SQLAlchemy

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        """Chuyển đổi object thành dictionary để response dạng JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description
        }
