import importlib.util
import os
import unittest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_path = os.path.join(base_dir, 'app1.py')
spec = importlib.util.spec_from_file_location('app', app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)

app = app_module.app
db = app_module.db
Customer = app_module.Customer
Product = app_module.Product
Order = app_module.Order
OrderItem = app_module.OrderItem
ContactMessage = app_module.ContactMessage


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def register(self, email='test@example.com', password='secret123',
                 full_name='Test User'):
        return self.client.post('/account', data={
            'action': 'register',
            'full_name': full_name,
            'email': email,
            'password': password,
        }, follow_redirects=True)

    def login(self, email='test@example.com', password='secret123'):
        return self.client.post('/account', data={
            'action': 'login',
            'email': email,
            'password': password,
        }, follow_redirects=True)

    def test_home_page_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_account_page_renders(self):
        response = self.client.get('/account')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<form', response.data)

    def test_shop_renders_products_from_db(self):
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            products = Product.query.all()
            self.assertGreater(len(products), 0)
            for product in products:
                self.assertIn(product.name.encode(), response.data)

    def test_account_registration_creates_customer(self):
        self.register()
        with app.app_context():
            customer = Customer.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(customer)
            self.assertEqual(customer.full_name, 'Test User')
            self.assertNotEqual(customer.password, 'secret123')

    def test_duplicate_email_is_rejected(self):
        self.register()
        response = self.register()
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            self.assertEqual(Customer.query.filter_by(email='test@example.com').count(), 1)

    def test_login_success_and_failure(self):
        self.register()
        response = self.login()
        self.assertIn(b'Welcome back', response.data)
        with self.client.session_transaction() as sess:
            self.assertIn('customer_id', sess)

        self.client.get('/logout')
        response = self.login(password='wrong-password')
        self.assertIn(b'Invalid email or password', response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn('customer_id', sess)

    def test_logout(self):
        self.register()
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn('customer_id', sess)

    def test_contact_creates_message(self):
        response = self.client.post('/contact', data={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Question',
            'message': 'Is the UltraBook in stock?',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            message = ContactMessage.query.filter_by(email='jane@example.com').first()
            self.assertIsNotNone(message)
            self.assertEqual(message.name, 'Jane Doe')

    def test_checkout_creates_order_with_items(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'city': 'Cairo',
            'phone': '+20123456789',
            'payment_method': 'Cash on Delivery',
            'total_amount': '1314.00',
            'cart_data': '[{"title": "Pro UltraBook X1", "price": 1299, "quantity": 1}, {"title": "Pulse Fit Band", "price": 99, "quantity": 1}]',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            order = Order.query.filter_by(email='salam@example.com').first()
            self.assertIsNotNone(order)
            self.assertEqual(order.total_amount, 1314.00)
            self.assertEqual(len(order.items), 2)
            self.assertEqual(order.items[0].title, 'Pro UltraBook X1')

    def test_checkout_rejects_empty_cart(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'cart_data': '[]',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            self.assertEqual(Order.query.count(), 0)

    def test_my_orders_requires_login(self):
        response = self.client.get('/my_orders')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/account', response.headers['Location'])

    def test_my_orders_shows_customer_orders(self):
        self.register()
        self.login()
        self.client.post('/checkout', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': '1 Test St',
            'city': 'Cairo',
            'phone': '+2',
            'payment_method': 'PayPal',
            'total_amount': '15.00',
            'cart_data': '[{"title": "Mouse", "price": 15, "quantity": 1}]',
        }, follow_redirects=True)
        response = self.client.get('/my_orders')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mouse', response.data)

    def test_order_detail_and_status_update(self):
        self.register()
        self.login()
        self.client.post('/checkout', data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': '1 Test St',
            'cart_data': '[{"title": "Mouse", "price": 15, "quantity": 1}]',
            'total_amount': '15.00',
        })
        with app.app_context():
            order_id = Order.query.first().id

        response = self.client.get(f'/order/{order_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order', response.data)

        response = self.client.post(
            f'/order/{order_id}/status/Delivered', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            self.assertEqual(db.session.get(Order, order_id).status, 'Delivered')


if __name__ == '__main__':
    unittest.main()