from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Perfume(db.Model):
    __tablename__ = 'perfumes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    cloudinary_url = db.Column(db.String(500), nullable=False)
    size = db.Column(db.String(50), default='50ml')
    notes = db.Column(db.String(300))  # e.g., "Rose, Oud, Sandalwood"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'cloudinary_url': self.cloudinary_url,
            'size': self.size,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_info_json = db.Column(db.JSON, nullable=False)  # {name, email, phone, address, city, state}
    items_json = db.Column(db.JSON, nullable=False)  # [{perfume_id, name, price, quantity}]
    total_price = db.Column(db.Float, nullable=False)
    payment_ref = db.Column(db.String(200), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_info': self.customer_info_json,
            'items': self.items_json,
            'total_price': self.total_price,
            'payment_ref': self.payment_ref,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
