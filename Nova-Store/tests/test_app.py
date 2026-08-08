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

    def test_contact_rejects_invalid_email(self):
        response = self.client.post('/contact', data={
            'name': 'Jane Doe',
            'email': 'not-an-email',
            'subject': 'Question',
            'message': 'Hello',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'valid email', response.data)
        with app.app_context():
            self.assertIsNone(ContactMessage.query.filter_by(email='not-an-email').first())

    def test_register_rejects_invalid_email(self):
        response = self.client.post('/account', data={
            'action': 'register',
            'full_name': 'Bad Email',
            'email': 'nope@@example..com',
            'password': 'secret123',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'valid email', response.data)
        with app.app_context():
            self.assertIsNone(Customer.query.filter_by(email='nope@@example..com').first())

    def test_checkout_rejects_invalid_email(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'not-an-email',
            'address': '123 Tech Street',
            'cart_data': '[{"title": "Pro UltraBook X1", "quantity": 1}]',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'valid email', response.data)
        with app.app_context():
            self.assertIsNone(Order.query.filter_by(email='not-an-email').first())

    def test_checkout_creates_order_with_items(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'city': 'Cairo',
            'phone': '+20123456789',
            'payment_method': 'Cash on Delivery',
            'total_amount': '0.01',
            'cart_data': '[{"title": "Pro UltraBook X1", "price": 1, "quantity": 1}, {"title": "Pulse Fit Band", "price": 1, "quantity": 1}]',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            order = Order.query.filter_by(email='salam@example.com').first()
            self.assertIsNotNone(order)
            self.assertEqual(order.total_amount, 1398.00)
            self.assertEqual(len(order.items), 2)
            self.assertEqual(order.items[0].title, 'Pro UltraBook X1')
            self.assertEqual(order.items[0].price, 1299.0)
            self.assertEqual(order.items[1].price, 99.0)
            self.assertIsNotNone(order.items[0].product_id)

    def test_checkout_rejects_forged_prices_and_negative_quantity(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'cart_data': '[{"title": "Pro UltraBook X1", "price": 0.01, "quantity": -5}]',
            'total_amount': '0.01',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            order = Order.query.filter_by(email='salam@example.com').first()
            self.assertIsNotNone(order)
            item = order.items[0]
            self.assertEqual(item.price, 1299.0)
            self.assertEqual(item.quantity, 1)
            self.assertEqual(order.total_amount, 1299.0)

    def test_checkout_merges_duplicate_items(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'cart_data': '[{"title": "Pro UltraBook X1", "price": 1, "quantity": 2}, {"title": "Pro UltraBook X1", "price": 7, "quantity": 3}]',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            order = Order.query.filter_by(email='salam@example.com').first()
            self.assertIsNotNone(order)
            self.assertEqual(len(order.items), 1)
            self.assertEqual(order.items[0].quantity, 5)
            self.assertEqual(order.total_amount, 1299.0 * 5)

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

    def test_checkout_handles_malformed_cart_data(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'cart_data': '[{"title": "Gadget", "price": "not-a-number", "quantity": "abc"}, "junk"]',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            order = Order.query.filter_by(email='salam@example.com').first()
            self.assertIsNotNone(order)
            self.assertEqual(len(order.items), 1)
            self.assertEqual(order.items[0].price, 0.0)
            self.assertEqual(order.items[0].quantity, 1)

    def test_checkout_handles_non_list_cart_data(self):
        response = self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'cart_data': '{"title": "Not an array"}',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            self.assertEqual(Order.query.count(), 0)

    def test_all_pages_render(self):
        for path in ['/', '/shop', '/about', '/contact', '/account', '/checkout']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, f'GET {path} failed')

    def test_static_assets_served(self):
        css = self.client.get('/static/style.css')
        try:
            self.assertEqual(css.status_code, 200)
        finally:
            css.close()
        js = self.client.get('/static/index.js')
        try:
            self.assertEqual(js.status_code, 200)
        finally:
            js.close()

    def test_order_has_created_at(self):
        self.client.post('/checkout', data={
            'first_name': 'Salam',
            'last_name': 'Mohamed',
            'email': 'salam@example.com',
            'address': '123 Tech Street',
            'cart_data': '[{"title": "Pro UltraBook X1", "price": 1, "quantity": 1}]',
        }, follow_redirects=True)
        with app.app_context():
            order = Order.query.filter_by(email='salam@example.com').first()
            self.assertIsNotNone(order)
            self.assertIsNotNone(order.created_at)

    def test_shop_has_search_empty_state(self):
        response = self.client.get('/shop')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="search-empty"', response.data)
        self.assertIn(b'No products found.', response.data)

    def test_flask_app_startup(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(app.config['TESTING'])
        self.assertIsNotNone(app.secret_key)
        with app.app_context():
            self.assertIsNotNone(db)
            self.assertEqual(Product.query.count(), 15)

    def test_exactly_15_products_in_database(self):
        self.client.get('/shop')
        with app.app_context():
            self.assertEqual(Product.query.count(), 15)

    def test_all_products_have_images_no_duplicates(self):
        self.client.get('/shop')
        with app.app_context():
            products = Product.query.all()
            images = [p.image_url for p in products]
            self.assertEqual(len(products), 15)
            self.assertTrue(all(images), 'every product must have an image')
            self.assertEqual(len(images), len(set(images)),
                             'no two products may share the same image')

    def test_search_bar_wired_on_shop_page(self):
        response = self.client.get('/shop')
        html = response.get_data(as_text=True)
        self.assertIn('id="searchInput"', html)
        self.assertIn('onkeyup="filterProducts()"', html)
        self.assertIn('data-search=', html)

    def test_filterproducts_defined_once_in_shared_js(self):
        js_path = os.path.join(base_dir, 'static', 'index.js')
        with open(js_path, encoding='utf-8') as fh:
            js = fh.read()
        self.assertEqual(js.count('function filterProducts'), 1,
                         'filterProducts() must be defined exactly once')

    def test_templates_start_with_doctype(self):
        templates_dir = os.path.join(base_dir, 'templates')
        for name in os.listdir(templates_dir):
            if not name.endswith('.html'):
                continue
            with open(os.path.join(templates_dir, name), encoding='utf-8') as fh:
                content = fh.read()
            self.assertTrue(
                content.lstrip().startswith('<!DOCTYPE html>'),
                f'{name} must start with <!DOCTYPE html> (got {content[:40]!r})')
            self.assertNotRegex(
                content, r'\[\d{1,2}/\d{1,2}/\d{4}', f'{name} contains pasted chat text')

    def test_url_for_endpoints_match_routes(self):
        with app.test_request_context():
            for endpoint in ['home', 'account', 'shop', 'checkout',
                             'contact', 'about', 'my_orders', 'logout']:
                url = app_module.url_for(endpoint)
                self.assertTrue(url.startswith('/'), f'{endpoint} -> {url}')

    def test_style_css_is_single_clean_copy(self):
        css_path = os.path.join(base_dir, 'static', 'style.css')
        with open(css_path, encoding='utf-8') as fh:
            css = fh.read()
        self.assertEqual(css.count('{'), css.count('}'),
                         'style.css must have balanced braces')
        self.assertEqual(css.count('@import'), 1,
                         'style.css must contain exactly one @import (no pasted duplicates)')

    def test_order_status_rejects_invalid_value(self):
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
        response = self.client.post(
            f'/order/{order_id}/status/Hacked', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():
            self.assertEqual(db.session.get(Order, order_id).status, 'Pending')

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