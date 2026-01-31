"""
Database Seed Script for Maison Écorce
Run this script to populate the database with sample perfumes
"""

from app import app, db
from models import Perfume

# Sample perfume data with high-quality images
SAMPLE_PERFUMES = [
    {
        "name": "Ébène Sauvage",
        "description": "A bold, mysterious fragrance that captures the essence of untamed wilderness. Opening with crisp bergamot and pink pepper, it evolves into a heart of smoky oud and rose absolute, before settling into a base of aged ebony wood and amber. Perfect for those who dare to stand out.",
        "price": 45000,
        "size": "50ml",
        "notes": "Bergamot, Pink Pepper, Oud, Rose, Ebony, Amber",
        "cloudinary_url": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&h=1000&fit=crop"
    },
    {
        "name": "Terre de Miel",
        "description": "Inspired by sun-drenched meadows, this warm, inviting scent combines the sweetness of wild honey with earthy vetiver roots. Notes of hay absolute and tonka bean create a comforting, enveloping aura that lingers beautifully on the skin.",
        "price": 38000,
        "size": "50ml",
        "notes": "Wild Honey, Vetiver, Hay, Tonka Bean, Sandalwood",
        "cloudinary_url": "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=800&h=1000&fit=crop"
    },
    {
        "name": "Mousse d'Aurore",
        "description": "The first light of dawn captured in a bottle. Fresh green moss mingles with dewdrops on violet leaves, while a delicate heart of iris and white tea creates an ethereal, almost mystical quality. A meditation on new beginnings.",
        "price": 42000,
        "size": "50ml",
        "notes": "Green Moss, Violet Leaf, Iris, White Tea, Musk",
        "cloudinary_url": "https://images.unsplash.com/photo-1595425964071-2c1ecb10e2ef?w=800&h=1000&fit=crop"
    },
    {
        "name": "Cèdre Céleste",
        "description": "A majestic composition that pays homage to ancient cedar forests. Rich Atlas cedar is elevated by hints of juniper and black pepper, while a base of incense and labdanum adds a sacred, contemplative dimension. Timeless and refined.",
        "price": 52000,
        "size": "50ml",
        "notes": "Atlas Cedar, Juniper, Black Pepper, Incense, Labdanum",
        "cloudinary_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=800&h=1000&fit=crop"
    },
    {
        "name": "Fleur de Nuit",
        "description": "When night-blooming jasmine meets the cool desert air. This intoxicating elixir weaves tuberose and jasmine sambac with mysterious notes of dark plum and narcissus. A seductive whisper that beckons after sunset.",
        "price": 48000,
        "size": "50ml",
        "notes": "Tuberose, Jasmine Sambac, Dark Plum, Narcissus, Musk",
        "cloudinary_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&h=1000&fit=crop"
    },
    {
        "name": "Sel Marin",
        "description": "The essence of coastal escapes. Mineral sea salt dances with driftwood and ambergris, while subtle notes of fig leaf and coconut water evoke lazy afternoons by hidden coves. Fresh, clean, utterly addictive.",
        "price": 35000,
        "size": "50ml",
        "notes": "Sea Salt, Driftwood, Ambergris, Fig Leaf, Coconut Water",
        "cloudinary_url": "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=800&h=1000&fit=crop"
    }
]

def seed_database():
    """Add sample perfumes to the database"""
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Check if products already exist
        existing = Perfume.query.first()
        if existing:
            print("Database already has products. Skipping seed.")
            return
        
        print("Seeding database with sample perfumes...")
        
        for data in SAMPLE_PERFUMES:
            perfume = Perfume(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                size=data["size"],
                notes=data["notes"],
                cloudinary_url=data["cloudinary_url"]
            )
            db.session.add(perfume)
        
        db.session.commit()
        print(f"Successfully added {len(SAMPLE_PERFUMES)} perfumes!")

if __name__ == "__main__":
    seed_database()
