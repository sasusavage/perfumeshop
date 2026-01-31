from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import uuid
from werkzeug.utils import secure_filename
import os
import requests
import json
import hashlib
import hmac
from config import Config
from config import Config
from models import db, Perfume, Order, SiteSettings

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # 1. Secure the filename
        original_filename = secure_filename(file.filename)
        
        # 2. Extract extension
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        
        # 3. Generate unique UUID filename
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # 4. Create full path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 5. Save file
        file.save(file_path)
        
        # 6. Return relative URL for database
        # In production this might need to be served via nginx or a dedicated route
        # For this setup we use Flask static serving
        return f"/static/uploads/{unique_filename}"
    return None

# Create tables on first request
with app.app_context():
    db.create_all()


# ============ AUTH DECORATOR ============
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============ CONTEXT PROCESSOR ============
@app.context_processor
def inject_settings():
    settings = SiteSettings.query.first()
    if not settings:
        # Create default if avoids crashing on first run
        settings = SiteSettings()
        # We don't save it here to avoid race conditions/readonly DB issues, 
        # but the object exists for variables.
        # Ideally, it should be seeded.
    return dict(site_settings=settings)


# ============ PUBLIC ROUTES ============
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    return render_template('product.html', product_id=product_id)


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html', paystack_public_key=app.config['PAYSTACK_PUBLIC_KEY'])


# ============ API ROUTES ============
@app.route('/api/perfumes', methods=['GET'])
def get_perfumes():
    perfumes = Perfume.query.order_by(Perfume.created_at.desc()).all()
    return jsonify([p.to_dict() for p in perfumes])


@app.route('/api/perfumes/<int:perfume_id>', methods=['GET'])
def get_perfume(perfume_id):
    perfume = Perfume.query.get_or_404(perfume_id)
    return jsonify(perfume.to_dict())


# ============ CART SESSION MANAGEMENT ============
@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', [])
    return jsonify(cart)


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    cart = session.get('cart', [])
    
    # Check if item already in cart
    for item in cart:
        if item['id'] == data['id']:
            item['quantity'] += data.get('quantity', 1)
            session['cart'] = cart
            return jsonify({'message': 'Cart updated', 'cart': cart})
    
    # Add new item
    cart.append({
        'id': data['id'],
        'name': data['name'],
        'price': data['price'],
        'image': data['image'],
        'quantity': data.get('quantity', 1)
    })
    session['cart'] = cart
    return jsonify({'message': 'Item added to cart', 'cart': cart})


@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    cart = session.get('cart', [])
    
    for item in cart:
        if item['id'] == data['id']:
            if data['quantity'] <= 0:
                cart.remove(item)
            else:
                item['quantity'] = data['quantity']
            break
    
    session['cart'] = cart
    return jsonify({'message': 'Cart updated', 'cart': cart})


@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != data['id']]
    session['cart'] = cart
    return jsonify({'message': 'Item removed', 'cart': cart})


@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return jsonify({'message': 'Cart cleared', 'cart': []})


# ============ PAYSTACK INTEGRATION ============
@app.route('/api/payment/initialize', methods=['POST'])
def initialize_payment():
    data = request.json
    cart = session.get('cart', [])
    
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    # Store customer info in session temporarily
    session['pending_customer_info'] = data['customer_info']
    session['pending_items'] = cart
    
    # Initialize Paystack transaction
    headers = {
        'Authorization': f"Bearer {app.config['PAYSTACK_SECRET_KEY']}",
        'Content-Type': 'application/json'
    }
    
    payload = {
        'email': data['customer_info']['email'],
        'amount': int(total * 100),  # Paystack uses kobo (cents)
        'callback_url': request.host_url.rstrip('/') + '/payment/callback',
        'metadata': {
            'customer_info': data['customer_info'],
            'items': cart
        }
    }
    
    response = requests.post(
        'https://api.paystack.co/transaction/initialize',
        headers=headers,
        json=payload
    )
    
    result = response.json()
    
    if result.get('status'):
        return jsonify({
            'authorization_url': result['data']['authorization_url'],
            'reference': result['data']['reference']
        })
    else:
        return jsonify({'error': 'Payment initialization failed'}), 400


@app.route('/payment/callback')
def payment_callback():
    reference = request.args.get('reference')
    
    if not reference:
        return render_template('payment_result.html', success=False, message='No reference provided')
    
    # Verify transaction with Paystack
    headers = {
        'Authorization': f"Bearer {app.config['PAYSTACK_SECRET_KEY']}"
    }
    
    response = requests.get(
        f'https://api.paystack.co/transaction/verify/{reference}',
        headers=headers
    )
    
    result = response.json()
    
    if result.get('status') and result['data']['status'] == 'success':
        # Create confirmed order
        metadata = result['data']['metadata']
        
        # Check if order already exists
        existing_order = Order.query.filter_by(payment_ref=reference).first()
        if not existing_order:
            order = Order(
                customer_info_json=metadata['customer_info'],
                items_json=metadata['items'],
                total_price=result['data']['amount'] / 100,
                payment_ref=reference,
                status='confirmed'
            )
            db.session.add(order)
            db.session.commit()
        
        # Clear cart
        session['cart'] = []
        session.pop('pending_customer_info', None)
        session.pop('pending_items', None)
        
        return render_template('payment_result.html', success=True, reference=reference)
    else:
        return render_template('payment_result.html', success=False, message='Payment verification failed')


@app.route('/api/paystack/webhook', methods=['POST'])
def paystack_webhook():
    # Verify webhook signature
    signature = request.headers.get('x-paystack-signature')
    
    if signature:
        computed = hmac.new(
            app.config['PAYSTACK_SECRET_KEY'].encode('utf-8'),
            request.data,
            hashlib.sha512
        ).hexdigest()
        
        if signature != computed:
            return jsonify({'error': 'Invalid signature'}), 400
    
    payload = request.json
    
    if payload.get('event') == 'charge.success':
        data = payload['data']
        reference = data['reference']
        
        # Check if order already exists
        existing_order = Order.query.filter_by(payment_ref=reference).first()
        if not existing_order:
            metadata = data.get('metadata', {})
            order = Order(
                customer_info_json=metadata.get('customer_info', {}),
                items_json=metadata.get('items', []),
                total_price=data['amount'] / 100,
                payment_ref=reference,
                status='confirmed'
            )
            db.session.add(order)
            db.session.commit()
    
    return jsonify({'status': 'ok'}), 200


# ============ ADMIN ROUTES ============
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid credentials')
    
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/orders')
@admin_required
def admin_orders():
    return render_template('admin/orders.html')


@app.route('/admin/products')
@admin_required
def admin_products():
    return render_template('admin/products.html')


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        # Process Text Fields
        settings.shop_name = request.form.get('shop_name', settings.shop_name)
        settings.hero_title = request.form.get('hero_title', settings.hero_title)
        settings.hero_subtitle = request.form.get('hero_subtitle', settings.hero_subtitle)
        settings.story_title = request.form.get('story_title', settings.story_title)
        settings.story_content = request.form.get('story_content', settings.story_content)
        
        # Process Images
        if 'hero_image' in request.files and request.files['hero_image'].filename != '':
            hero_file = request.files['hero_image']
            hero_url = save_uploaded_file(hero_file)
            if hero_url:
                settings.hero_image = hero_url
                
        if 'story_image' in request.files and request.files['story_image'].filename != '':
            story_file = request.files['story_image']
            story_url = save_uploaded_file(story_file)
            if story_url:
                settings.story_image = story_url
        
        db.session.commit()
        return redirect(url_for('admin_settings'))
        
    return render_template('admin/settings.html', settings=settings)


# ============ ADMIN API ROUTES ============
@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def get_admin_orders():
    status = request.args.get('status', 'confirmed')
    if status == 'all':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(status=status).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.json
    order.status = data['status']
    db.session.commit()
    return jsonify(order.to_dict())


@app.route('/api/admin/perfumes', methods=['POST'])
@admin_required
def add_perfume():
    # Handle image upload
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    # Save file locally
    image_url = save_uploaded_file(file)
    
    if not image_url:
        return jsonify({'error': 'Invalid file type or upload failed'}), 400
    
    # Create perfume record
    perfume = Perfume(
        name=request.form['name'],
        description=request.form['description'],
        price=float(request.form['price']),
        cloudinary_url=image_url,  # We keep the column name for compatibility but store local path
        size=request.form.get('size', '50ml'),
        notes=request.form.get('notes', '')
    )
    
    db.session.add(perfume)
    db.session.commit()
    
    return jsonify(perfume.to_dict()), 201


@app.route('/api/admin/perfumes/<int:perfume_id>', methods=['PUT'])
@admin_required
def update_perfume(perfume_id):
    perfume = Perfume.query.get_or_404(perfume_id)
    
    # Handle optional image upload
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        image_url = save_uploaded_file(file)
        
        if image_url:
            # Optional: Delete old file here if it exists and is local
            perfume.cloudinary_url = image_url
        else:
             return jsonify({'error': 'Invalid file type'}), 400
    
    perfume.name = request.form.get('name', perfume.name)
    perfume.description = request.form.get('description', perfume.description)
    perfume.price = float(request.form.get('price', perfume.price))
    perfume.size = request.form.get('size', perfume.size)
    perfume.notes = request.form.get('notes', perfume.notes)
    
    db.session.commit()
    return jsonify(perfume.to_dict())


@app.route('/api/admin/perfumes/<int:perfume_id>', methods=['DELETE'])
@admin_required
def delete_perfume(perfume_id):
    perfume = Perfume.query.get_or_404(perfume_id)
    db.session.delete(perfume)
    db.session.commit()
    return jsonify({'message': 'Perfume deleted'})


@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    total_orders = Order.query.filter_by(status='confirmed').count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).filter_by(status='confirmed').scalar() or 0
    total_products = Perfume.query.count()
    
    return jsonify({
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products
    })


if __name__ == '__main__':
    app.run(debug=True, port=5002)
