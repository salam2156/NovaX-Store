from flask import Flask, render_template, request, redirect, url_for  # type: ignore[import]
from flask_sqlalchemy import SQLAlchemy  # type: ignore[import]

# إعداد تطبيق فلاسك
app = Flask(__name__)

# إعداد قاعدة البيانات SQLite (سيتم إنشاء ملف store.db تلقائياً)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف جدول الطلبات (Orders) لحفظ بيانات الـ Checkout
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    def repr(self):
        return f'<Order {self.id}>'

# إنشاء قاعدة البيانات والجداول عند تشغيل السيرفر لأول مرة
with app.app_context():
    db.create_all()

# مسار الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# مسار صفحة الشيك أوت لاستقبال البيانات وحفظها
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # استقبال البيانات الواردة من الفورم
        f_name = request.form.get('first_name')
        l_name = request.form.get('last_name')
        user_email = request.form.get('email')
        user_address = request.form.get('address')
        total = request.form.get('total_amount', 0.0)

        # حفظ الطلب في قاعدة البيانات
        new_order = Order(
            first_name=f_name, 
            last_name=l_name, 
            email=user_email, 
            address=user_address, 
            total_amount=float(total)
        )
        db.session.add(new_order)
        db.session.commit()

        return "Order placed and saved to database successfully!"
    
    return render_template('checkout.html')

if __name__ == 'main':
    app.run(debug=True)