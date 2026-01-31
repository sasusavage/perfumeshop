from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Perfume(db.Model):
    __tablename__ = 'perfumes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    compare_at_price = db.Column(db.Float, nullable=True)  # Original price for discounts
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
            'compare_at_price': self.compare_at_price,
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

class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Global
    shop_name = db.Column(db.String(100), default="Maison Écorce")
    
    # Hero Section
    hero_title = db.Column(db.String(200), default="Nature Distilled")
    hero_subtitle = db.Column(db.String(300), default="Experience the raw elegance of botanical perfumery.")
    hero_image = db.Column(db.String(500), default="https://images.unsplash.com/photo-1541643600914-78b084683601?w=1920&q=80")
    
    # About/Story Section
    story_title = db.Column(db.String(200), default="Our Story")
    story_content = db.Column(db.Text, default="Founded in Grasse, Maison Écorce represents the convergence of traditional craftsmanship and modern sustainability. We source our ingredients from ethically managed forests and gardens, ensuring that every bottle tells a story of the earth.")
    story_image = db.Column(db.String(500), default="https://images.unsplash.com/photo-1615634260167-c8cdede054de?w=800&q=80")
    
    # Newsletter Section
    newsletter_title = db.Column(db.String(200), default="Join Our World")
    newsletter_subtitle = db.Column(db.String(300), default="Be the first to discover new fragrances, exclusive offers, and the stories behind our scents.")

    def to_dict(self):
        return {
            'shop_name': self.shop_name,
            'hero_title': self.hero_title,
            'hero_subtitle': self.hero_subtitle,
            'hero_image': self.hero_image,
            'story_title': self.story_title,
            'story_content': self.story_content,
            'story_image': self.story_image,
            'newsletter_title': self.newsletter_title,
            'newsletter_subtitle': self.newsletter_subtitle
        }
