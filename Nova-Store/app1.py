from flask import Flask, render_template, request, redirect, url_for  # type: ignore[reportMissingImports]

try:
    from flask_sqlalchemy import SQLAlchemy  # type: ignore[reportMissingImports]
except ImportError as exc:
    raise ImportError(
        "Flask-SQLAlchemy is not installed. Install it using 'pip install Flask-SQLAlchemy' and try again."
    ) from exc

# Create Flask app
app = Flask(__name__) # تم تصحيح name

# إعداد قاعدة البيانات SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ربط SQLAlchemy بالتطبيق
db = SQLAlchemy()
db.init_app(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def repr(self):
        return f"<Customer {self.full_name}>"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    def repr(self):
        return f"<Order {self.id}>"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))

    def repr(self):
        return f"<Product {self.name}>"

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)

    def repr(self):
        return f"<ContactMessage {self.name}>"

with app.app_context():
    db.create_all()

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Shop Page
@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        new_message = ContactMessage(name=name, email=email, subject=subject, message=message)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('contact'))
    return render_template('contact.html')

# index Page
@app.route('/index', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        customer = Customer(full_name=full_name, email=email, password=password)
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('account')) # تم تصحيح الـ url_for
    return render_template('account.html')

# Checkout Page
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        first_name = request.form.get('first_name') # تم تصحيح المسافة البادئة
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        address = request.form.get('address')
        total_amount = request.form.get('total_amount')
        order = Order(first_name=first_name, last_name=last_name, email=email, address=address, total_amount=float(total_amount))
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('checkout.html')