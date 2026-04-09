import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='user') # admin, user
    scopes = db.Column(db.String(255), default='[]') # JSON list of scopes: e.g., ["read:item", "write:item"]
    
    items = db.relationship('Item', backref='owner', lazy=True)

    def set_scopes(self, scopes_list):
        self.scopes = json.dumps(scopes_list)

    def get_scopes(self):
        try:
            return json.loads(self.scopes)
        except:
            return []

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
