import hashlib
import json
import os
import time
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError as exc:
    raise ImportError(
        "Flask-SQLAlchemy is not installed. Install it using 'pip install Flask-SQLAlchemy' and try again."
    ) from exc

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nova-store-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///store.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================
# Business rules (single source of truth for the cart/order flow)
# ==========================
SHIPPING_FEE = 15.00                       # flat shipping cost, mirrored in index.js
MAX_QUANTITY_PER_ITEM = 99                 # hard cap on units of one product per cart
MAX_TOTAL_UNITS = 500                      # hard cap on units across the whole order
ORDER_DEDUPE_WINDOW_SECONDS = 30           # reject identical resubmissions within this window
PRICE_TOLERANCE = 0.01                     # allowed drift when verifying the client total


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.full_name}>"


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    items = db.relationship('OrderItem', backref='order', lazy=True,
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Order {self.id}>"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<OrderItem {self.title}>"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50))

    def __repr__(self):
        return f"<Product {self.name}>"


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<ContactMessage {self.name}>"


# ==========================
# Database bootstrap
# ==========================

PRODUCT_SEED = [
    ("Pro UltraBook X1", "Powerful 16GB RAM, 512GB SSD, stunning 4K display for creators.", 1299, "https://images.unsplash.com/photo-1517336714731-489689fd1ca8", "Laptops"),
    ("Gaming Beast G15", "Dedicated graphics card, high refresh rate, built for extreme gaming.", 1599, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853", "Laptops"),
    ("SlimBook Air", "Ultra-thin, lightweight design with all-day battery life for professionals.", 999, "https://images.unsplash.com/photo-1541807084-5c52b6b3adef", "Laptops"),
    ("NovaPhone 14 Pro", "Triple camera setup, 120Hz OLED screen, massive storage capacity.", 899, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9", "Smartphones"),
    ("Apex X Phone", "Sleek futuristic design with lightning-fast processor and 5G support.", 749, "https://images.unsplash.com/photo-1565849904461-04a58ad377e0", "Smartphones"),
    ("Pulse Lite 5G", "Affordable performance with great battery life and sharp dual cameras.", 499, "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37", "Smartphones"),
    ("SonicBass Wireless", "Active noise cancellation, deep bass, and 40 hours of continuous playback.", 249, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e", "Audio & Headphones"),
    ("AirPods Pro Max", "True wireless earbuds with spatial audio and crystal-clear microphone.", 199, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df", "Audio & Headphones"),
    ("Studio Pro Monitors", "Over-ear studio headphones designed for professional audio mixing.", 299, "https://images.unsplash.com/photo-1546435770-a3e426bf472b", "Audio & Headphones"),
    ("Titan SmartWatch 3", "Fitness tracking, heart rate monitor, GPS, and waterproof build.", 299, "https://images.unsplash.com/photo-1523275335684-37898b6baf30", "Wearables"),
    ("Pulse Fit Band", "Lightweight smart band to track your daily steps, sleep, and calories.", 99, "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1", "Wearables"),
    ("CyberSport Edition", "Rugged outdoor smartwatch designed for extreme athletes and explorers.", 349, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a", "Wearables"),
    ("CyberPad Controller", "Ergonomic wireless gamepad with customizable triggers and RGB lighting.", 79, "https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf", "Gaming Gear"),
    ("MechRGB Keyboard", "Mechanical switches, custom RGB backlight, and anti-ghosting keys.", 129, "https://images.unsplash.com/photo-1587829741301-dc798b83add3", "Gaming Gear"),
    ("Viper Precision Mouse", "Ultra-lightweight gaming mouse with high DPI sensor and fast response.", 89, "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7", "Gaming Gear"),
]

CATEGORY_LABELS = {
    "Laptops": "High-Performance Laptops",
    "Smartphones": "Smartphones & Devices",
    "Audio & Headphones": "Audio & Headphones",
    "Wearables": "Smart Wearables",
    "Gaming Gear": "Gaming Gear",
}


def _table_columns(table_name):
    rows = db.session.execute(
        text('PRAGMA table_info("{}")'.format(table_name))
    ).fetchall()
    return [row[1] for row in rows]


def _add_column_if_missing(table_name, column_name, column_ddl):
    if column_name not in _table_columns(table_name):
        db.session.execute(
            text('ALTER TABLE "{}" ADD COLUMN {} {}'.format(table_name, column_name, column_ddl))
        )
        db.session.commit()


def _migrate_existing_tables():
    # The PRAGMA-based column migration is SQLite-specific.
    if db.engine.dialect.name != 'sqlite':
        return
    tables = [row[0] for row in db.session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table'")
    ).fetchall()]
    if 'order' in tables:
        _add_column_if_missing('order', 'customer_id', 'INTEGER REFERENCES customer(id)')
        _add_column_if_missing('order', 'city', 'VARCHAR(100)')
        _add_column_if_missing('order', 'phone', 'VARCHAR(50)')
        _add_column_if_missing('order', 'payment_method', 'VARCHAR(50)')
        _add_column_if_missing('order', 'status', 'VARCHAR(20) DEFAULT \'Pending\'')
        _add_column_if_missing('order', 'created_at', 'DATETIME')
    if 'product' in tables:
        _add_column_if_missing('product', 'category', 'VARCHAR(50)')
    if 'order_item' in tables:
        _add_column_if_missing('order_item', 'product_id',
                               'INTEGER REFERENCES product(id)')


def _seed_products():
    existing_by_name = {p.name: p for p in Product.query.all()}
    for name, description, price, image_url, category in PRODUCT_SEED:
        product = existing_by_name.get(name)
        if product is None:
            db.session.add(Product(name=name, description=description,
                                   price=price, image_url=image_url,
                                   category=category))
        elif product.category is None:
            product.category = category
    db.session.commit()


def init_db():
    db.create_all()
    _migrate_existing_tables()
    _seed_products()


_db_initialized = False


@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        _db_initialized = True
        with app.app_context():
            init_db()
    else:
        with app.app_context():
            has_product_table = db.session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='product'")
            ).scalar()
            if has_product_table and Product.query.count() == 0:
                _seed_products()


# ==========================
# Helpers / auth
# ==========================

def _is_valid_email(email):
    email = (email or '').strip()
    if email.count('@') != 1:
        return False
    local, _, domain = email.partition('@')
    if not local or not domain:
        return False
    return '.' in domain and not domain.startswith('.') and not domain.endswith('.')


def _normalise_quantity(raw):
    """Return an int >= 1, or None if the value is missing/invalid.

    Quantities are parsed client-side by the UI but MUST be re-validated here:
    malicious clients can post any string (e.g. "0", "-5", "abc" or
    "999999"), which would previously create absurd or free line items.
    """
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        return None
    if quantity < 1:
        return None
    return quantity


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access that page.', 'error')
            return redirect(url_for('account'))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_current_customer():
    customer = None
    customer_id = session.get('customer_id')
    if customer_id:
        customer = db.session.get(Customer, customer_id)
    return {'current_customer': customer}


# ==========================
# Pages
# ==========================

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/shop')
def shop():
    """Serve the catalogue straight from the database.

    The shop template renders prices/cards from Product rows, so the storefront,
    the cart and the checkout all derive from the same source of truth. Prices
    are re-validated against the database again at checkout; a hardcoded,
    desynchronised value can never get charged.
    """
    products = Product.query.order_by(Product.category, Product.name).all()
    grouped = {}
    for product in products:
        grouped.setdefault(product.category or 'Other', []).append(product)
    return render_template('shop.html', grouped=grouped,
                           category_labels=CATEGORY_LABELS)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip()
        subject = (request.form.get('subject') or '').strip()
        message = (request.form.get('message') or '').strip()

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('contact'))

        if not _is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('contact'))

        new_message = ContactMessage(name=name, email=email,
                                     subject=subject, message=message)
        db.session.add(new_message)
        db.session.commit()
        flash('Your message has been sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            email = (request.form.get('email') or '').strip()
            password = request.form.get('password') or ''

            customer = Customer.query.filter_by(email=email).first()
            if customer and check_password_hash(customer.password, password):
                session['customer_id'] = customer.id
                flash(f'Welcome back, {customer.full_name}!', 'success')
                return redirect(url_for('home'))

            flash('Invalid email or password.', 'error')
            return redirect(url_for('account'))

        full_name = (request.form.get('full_name') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''

        if not full_name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('account'))

        if not _is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('account'))

        customer = Customer(full_name=full_name, email=email,
                            password=generate_password_hash(password))
        try:
            db.session.add(customer)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('An account with that email already exists. Please log in instead.', 'error')
            return redirect(url_for('account'))

        session['customer_id'] = customer.id
        flash(f'Account created successfully. Welcome, {full_name}!', 'success')
        return redirect(url_for('home'))

    return render_template('account.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        first_name = (request.form.get('first_name') or '').strip()
        last_name = (request.form.get('last_name') or '').strip()
        email = (request.form.get('email') or '').strip()
        address = (request.form.get('address') or '').strip()
        city = (request.form.get('city') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        payment_method = request.form.get('payment_method') or ''
        cart_data = request.form.get('cart_data') or '[]'

        try:
            cart = json.loads(cart_data)
            if not isinstance(cart, list):
                cart = []
        except (ValueError, TypeError):
            cart = []

        if not first_name or not last_name or not email or not address:
            flash('Please complete your billing details.', 'error')
            return redirect(url_for('checkout'))

        if not _is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('checkout'))

        if not cart:
            flash('Your cart is empty. Add some products before placing an order.', 'error')
            return redirect(url_for('checkout'))

        # ----------------------------------------------------------------
        # Rebuild the order from the DATABASE (single source of truth).
        # Titles are only used to look products up; quantities are capped;
        # prices always come from the Product row, never from the client.
        # Unknown titles / zero-priced products are rejected outright, so a
        # tampered or stale cart can never create "free" line items.
        # ----------------------------------------------------------------
        products_by_title = {p.name: p for p in Product.query.all()}
        merged = {}      # keyed by product id
        total_units = 0

        for item in cart:
            if not isinstance(item, dict):
                continue
            title = str(item.get('title') or '').strip()
            if not title:
                continue
            product = products_by_title.get(title)
            if product is None or product.price <= 0:
                flash(
                    'One of the items in your cart is no longer available. '
                    'Please review your cart and try again.',
                    'error',
                )
                return redirect(url_for('checkout'))

            quantity = _normalise_quantity(item.get('quantity'))
            if quantity is None:
                flash('One of the items in your cart has an invalid quantity. '
                      'Please review your cart and try again.', 'error')
                return redirect(url_for('checkout'))
            if quantity > MAX_QUANTITY_PER_ITEM:
                flash(f'{title} exceeds the maximum orderable quantity '
                      f'({MAX_QUANTITY_PER_ITEM} units per item).', 'error')
                return redirect(url_for('checkout'))

            if product.id in merged:
                merged[product.id]['quantity'] += quantity
            else:
                merged[product.id] = {
                    'product': product,
                    'quantity': quantity,
                }
            total_units += quantity
            if total_units > MAX_TOTAL_UNITS:
                flash(f'Your order exceeds the maximum allowed quantity '
                      f'({MAX_TOTAL_UNITS} units).', 'error')
                return redirect(url_for('checkout'))

        if not merged:
            flash('Your cart does not contain any valid items.', 'error')
            return redirect(url_for('checkout'))

        # Verify that merged line quantities are still within the per-item cap
        # (duplicate lines could otherwise combine past the limit).
        for entry in merged.values():
            if entry['quantity'] > MAX_QUANTITY_PER_ITEM:
                flash(f'{entry["product"].name} exceeds the maximum orderable '
                      f'quantity ({MAX_QUANTITY_PER_ITEM} units per item).', 'error')
                return redirect(url_for('checkout'))

        subtotal = round(sum(
            entry['product'].price * entry['quantity']
            for entry in merged.values()
        ), 2)
        total_amount = round(subtotal + SHIPPING_FEE, 2)

        # Cross-check the hidden total built client-side. If it disagrees with
        # the authoritative server total, someone tampered with the form or a
        # catalogue price changed mid-checkout - refuse instead of charging a
        # price nobody agreed on.
        try:
            client_total = float(request.form.get('total_amount') or '')
        except (TypeError, ValueError):
            client_total = None
        if client_total is not None and abs(client_total - total_amount) > PRICE_TOLERANCE:
            flash('Your cart total changed and could not be verified. '
                  'Please review your cart and try again.', 'error')
            return redirect(url_for('checkout'))

        # ----------------------------------------------------------------
        # Server-side double-submit guard.
        # The JS on the checkout page also blocks a second click, but a
        # network re-post or a scripted client can ignore that. We build a
        # fingerprint of the order contents and refuse to create the same
        # order twice within a short window on the same session.
        # ----------------------------------------------------------------
        dedupe_lines = sorted(
            (entry['product'].name, entry['quantity']) for entry in merged.values()
        )
        dedupe_key = hashlib.sha256(
            '|'.join([
                first_name.lower(), last_name.lower(), email.lower(),
                address.lower(), json.dumps(dedupe_lines, sort_keys=True),
            ]).encode('utf-8')
        ).hexdigest()

        last_ts = session.get('last_order_ts')
        if (last_ts is not None
                and session.get('last_order_key') == dedupe_key
                and time.time() - last_ts < ORDER_DEDUPE_WINDOW_SECONDS):
            flash('Your order has already been placed. '
                  'Please do not resubmit the form.', 'error')
            return redirect(url_for('checkout'))

        # Link the order to the logged-in customer, or to a customer matching
        # the billing email so guests can still find it under "My Orders".
        customer_id = session.get('customer_id')
        if customer_id is None:
            matched_customer = Customer.query.filter(
                db.func.lower(Customer.email) == email.lower()
            ).first()
            if matched_customer is not None:
                customer_id = matched_customer.id

        order = Order(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            city=city,
            phone=phone,
            payment_method=payment_method,
            total_amount=total_amount,
            status='Pending',
        )
        for entry in merged.values():
            product = entry['product']
            order.items.append(OrderItem(
                product_id=product.id,
                title=product.name,
                quantity=entry['quantity'],
                price=product.price,
            ))

        db.session.add(order)
        db.session.commit()

        # Remember this exact order so a re-post cannot create a duplicate.
        session['last_order_key'] = dedupe_key
        session['last_order_ts'] = time.time()

        flash(f'Order #{order.id} placed successfully! '
              'Thank you for shopping with Nova-Store.', 'success')
        return redirect(url_for('home', order_placed=1, order_id=order.id))

    return render_template('checkout.html')


@app.route('/my_orders')
@login_required
def my_orders():
    customer = db.session.get(Customer, session['customer_id'])
    orders = (Order.query
              .filter(db.or_(
                  Order.customer_id == customer.id,
                  db.and_(
                      Order.customer_id.is_(None),
                      db.func.lower(Order.email) == customer.email.lower()
                  )
              ))
              .order_by(Order.id.desc())
              .all())
    entries = [{'order': order, 'order_items': order.items} for order in orders]
    return render_template('my_orders.html', orders=entries)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = (Order.query
             .filter_by(id=order_id, customer_id=session['customer_id'])
             .first_or_404())
    return render_template('order_detail.html', order=order, items=order.items)


@app.route('/order/<int:order_id>/status/<string:status>', methods=['POST'])
@login_required
def update_order_status(order_id, status):
    order = (Order.query
             .filter_by(id=order_id, customer_id=session['customer_id'])
             .first_or_404())
    if status not in ('Pending', 'Shipped', 'Delivered'):
        flash('Invalid order status.', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    order.status = status
    db.session.commit()
    flash(f'Order #{order.id} marked as {status}.', 'success')
    return redirect(url_for('order_detail', order_id=order.id))


if __name__ == '__main__':
    app.run(debug=True)