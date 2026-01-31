# Maison Écorce - Luxury Perfume Boutique

A sleek, minimalist e-commerce mini-site for a boutique perfume brand. Built with Flask, PostgreSQL, Cloudinary, and Paystack.

![Design Language: Nature Distilled](https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&h=400&fit=crop)

## ✨ Features

- **Guest-Only Checkout**: Session-based cart with no account creation required
- **Paystack Integration**: Secure payment processing with webhook verification
- **Admin Dashboard**: Manage products, view orders, update statuses
- **Cloudinary Integration**: Direct image upload for product management
- **Responsive Design**: Beautiful on all devices

## 🎨 Design Philosophy

The design follows a "Nature Distilled" aesthetic:
- **Color Palette**: Muted earth tones (Charcoal, Clay, Sand, Cream, Ivory)
- **Typography**: Cormorant Garamond (serif headers) + Outfit (sans-serif body)
- **Layout**: Generous negative space, large product cards, editorial feel

## 🛠 Tech Stack

- **Backend**: Python Flask with Flask-SQLAlchemy
- **Database**: PostgreSQL
- **Image Hosting**: Cloudinary
- **Payment**: Paystack
- **Frontend**: Vanilla HTML, CSS, JavaScript

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- Cloudinary account
- Paystack account

### 1. Clone and Setup

```bash
# Navigate to project
cd harry

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Flask
FLASK_SECRET_KEY=your-super-secret-key-here

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/perfume_db

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Paystack
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### 3. Create Database

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE perfume_db;
\q
```

### 4. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## 🗂 Project Structure

```
harry/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
│
├── static/
│   ├── css/
│   │   └── style.css      # Complete design system
│   └── js/
│       ├── cart.js        # Cart management
│       └── main.js        # UI utilities
│
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Homepage
    ├── shop.html          # Product listing
    ├── product.html       # Product detail
    ├── cart.html          # Shopping cart
    ├── checkout.html      # Checkout with Paystack
    ├── payment_result.html # Payment confirmation
    │
    └── admin/
        ├── login.html     # Admin login
        ├── base.html      # Admin base template
        ├── dashboard.html # Admin dashboard
        ├── orders.html    # Order management
        └── products.html  # Product management
```

## 🔐 Admin Access

Access the admin dashboard at `/admin`

Default credentials (change in production):
- Username: `admin`
- Password: `admin123`

## 💳 Payment Flow

1. Customer fills checkout form
2. Backend initializes Paystack transaction
3. Customer is redirected to Paystack checkout
4. On success, Paystack redirects to callback URL
5. Backend verifies payment and creates confirmed order
6. Webhook provides additional verification (recommended for production)

### Paystack Webhook Setup

Set your webhook URL in Paystack dashboard:
```
https://yourdomain.com/api/paystack/webhook
```

## 📝 API Endpoints

### Public
- `GET /api/perfumes` - List all perfumes
- `GET /api/perfumes/<id>` - Get single perfume
- `GET /api/cart` - Get cart contents
- `POST /api/cart/add` - Add item to cart
- `POST /api/cart/update` - Update item quantity
- `POST /api/cart/remove` - Remove item from cart
- `POST /api/payment/initialize` - Initialize Paystack payment

### Admin (requires authentication)
- `GET /api/admin/orders` - List orders
- `PUT /api/admin/orders/<id>/status` - Update order status
- `POST /api/admin/perfumes` - Add new perfume
- `PUT /api/admin/perfumes/<id>` - Update perfume
- `DELETE /api/admin/perfumes/<id>` - Delete perfume
- `GET /api/admin/stats` - Dashboard statistics

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**: Set secure values for all secrets
2. **Database**: Use managed PostgreSQL (e.g., Heroku Postgres, AWS RDS)
3. **Cloudinary**: Configure production cloud
4. **Paystack**: Switch to live keys
5. **HTTPS**: Ensure all traffic is encrypted
6. **Session**: Configure secure session storage

### Deploy to Heroku

```bash
# Create Heroku app
heroku create maison-ecorce

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set FLASK_SECRET_KEY=...
heroku config:set CLOUDINARY_CLOUD_NAME=...
# ... set all other variables

# Deploy
git push heroku main
```

## 📄 License

MIT License - Feel free to use for personal or commercial projects.

---

Built with ❤️ for the love of beautiful fragrances.
